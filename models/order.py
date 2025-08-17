# models/order.py
from utils.rds_helper import RDSHelper
from datetime import datetime
from decimal import Decimal

class Order:
    def __init__(self):
        self.db_helper = RDSHelper()

    def create_order_with_items(self, customer_id, po_number, item_ids):
        order_sql = "INSERT INTO orders (customer_id, po_number) VALUES (%s, %s) RETURNING id"
        
        conn = self.db_helper.connection
        try:
            with conn.cursor() as cur:
                cur.execute(order_sql, (customer_id, po_number))
                order_id = cur.fetchone()[0]
                
                total_order_amount = Decimal('0.0')
                
                item_details_sql = "SELECT * FROM enquiry_items WHERE id = ANY(%s::int[])"
                cur.execute(item_details_sql, (item_ids,))
                
                cols = [desc[0] for desc in cur.description]
                enquiry_items = [dict(zip(cols, row)) for row in cur.fetchall()]
                
                order_item_insert_sql = """
                    INSERT INTO order_items (order_id, enquiry_item_id, wo_number, drawing_number, part_number, 
                    material_type, quantity, unit_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                for i, item in enumerate(enquiry_items):
                    wo_number = f"WO-{order_id}-{i+1}"
                    cur.execute(order_item_insert_sql, (
                        order_id, item['id'], wo_number, item['drawing_number'], item['part_number'],
                        item['material_type'], item['quantity'], item['unit_price']
                    ))
                    total_order_amount += (item['unit_price'] * item['quantity'])

                update_total_sql = "UPDATE orders SET total_amount = %s WHERE id = %s"
                cur.execute(update_total_sql, (total_order_amount, order_id))
                
            conn.commit()
            return order_id
        except Exception as e:
            conn.rollback()
            raise e

    def get_all_orders_summary(self):
        sql = """
            SELECT o.id, o.po_number, o.status, o.total_amount, c.name as customer_name, o.order_date
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE o.deactivated_at IS NULL
            ORDER BY o.created_at DESC
        """
        return self.db_helper.execute_statement(sql)

    def get_order_details_with_items(self, order_id):
        order_sql = "SELECT o.*, c.name as customer_name FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.id = %s"
        items_sql = "SELECT * FROM order_items WHERE order_id = %s AND deactivated_at IS NULL ORDER BY id"
        
        order = self.db_helper.execute_statement(order_sql, (order_id,))
        items = self.db_helper.execute_statement(items_sql, (order_id,))
        
        return (order[0], items) if order else (None, [])

    def update_overall_status(self, order_id):
        items_sql = "SELECT status FROM order_items WHERE order_id = %s AND deactivated_at IS NULL"
        items = self.db_helper.execute_statement(items_sql, (order_id,))
        
        if not items:
            return

        statuses = {item['status'] for item in items}
        new_status = 'pending'
        
        if all(s == 'completed' for s in statuses):
            new_status = 'completed'
        elif any(s == 'processing' for s in statuses) or any(s == 'completed' for s in statuses):
            new_status = 'processing'
        elif all(s == 'cancelled' for s in statuses):
            new_status = 'cancelled'

        update_sql = "UPDATE orders SET status = %s WHERE id = %s"
        self.db_helper.execute_command(update_sql, (new_status, order_id))

    def update_item_status(self, item_id, status):
        sql = "UPDATE order_items SET status = %s WHERE id = %s RETURNING order_id"
        # Since execute_command doesn't return results, we use execute_statement
        cursor = self.db_helper.connection.cursor()
        try:
            cursor.execute(sql, (status, item_id))
            order_id = cursor.fetchone()[0]
            self.db_helper.connection.commit()
            cursor.close()
            # After updating an item, re-evaluate the parent order's status
            if order_id:
                self.update_overall_status(order_id)
        except Exception as e:
            self.db_helper.connection.rollback()
            cursor.close()
            raise e
        
    def get_completed_items_for_customer(self, customer_id):
        sql = """
            SELECT oi.*, o.po_number
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE o.customer_id = %s AND oi.status = 'completed' AND o.deactivated_at IS NULL
            AND oi.id NOT IN (SELECT order_item_id FROM invoice_items WHERE order_item_id IS NOT NULL)
        """
        return self.db_helper.execute_statement(sql, (customer_id,))
    
    def get_deactivated(self):
        sql = """
            SELECT o.id, o.po_number, o.status, c.name as customer_name, o.deactivated_at
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            WHERE o.deactivated_at IS NOT NULL
            ORDER BY o.deactivated_at DESC
        """
        return self.db_helper.execute_statement(sql)