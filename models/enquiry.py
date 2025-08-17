# models/enquiry.py
from utils.rds_helper import RDSHelper
from datetime import datetime

class Enquiry:
    def __init__(self):
        self.db_helper = RDSHelper()

    def create_enquiry_with_items(self, customer_id, enq_number, items):
        enquiry_sql = "INSERT INTO enquiries (customer_id, enq_number) VALUES (%s, %s) RETURNING id"
        
        self.db_helper.is_connection_alive()
        conn = self.db_helper.connection
        try:
            with conn.cursor() as cur:
                cur.execute(enquiry_sql, (customer_id, enq_number))
                enquiry_id = cur.fetchone()[0]

                item_sql = """
                INSERT INTO enquiry_items (enquiry_id, drawing_number, part_number, part_revision_number, 
                material_type, material_specification, with_material, unit_price, quantity, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                for item in items:
                    with_material_bool = True if item.get('with_material') == 'yes' else False
                    cur.execute(item_sql, (
                        enquiry_id, item['drawing_number'], item['part_number'], item['part_revision_number'],
                        item['material_type'], item['material_specification'], with_material_bool,
                        float(item['unit_price']), int(item['quantity']), item['remarks']
                    ))
            conn.commit()
            return enquiry_id
        except Exception as e:
            conn.rollback()
            raise e

    def get_all(self):
        sql = """
            SELECT e.id, e.enq_number, e.status, c.name as customer_name, e.created_at,
                   COUNT(ei.id) as item_count
            FROM enquiries e
            JOIN customers c ON e.customer_id = c.id
            LEFT JOIN enquiry_items ei ON e.id = ei.enquiry_id AND ei.deactivated_at IS NULL
            WHERE e.deactivated_at IS NULL
            GROUP BY e.id, c.name
            ORDER BY e.created_at DESC
        """
        return self.db_helper.execute_statement(sql)

    def get_details_by_id(self, enquiry_id):
        enquiry_sql = "SELECT e.*, c.name as customer_name FROM enquiries e JOIN customers c ON e.customer_id = c.id WHERE e.id = %s"
        items_sql = "SELECT * FROM enquiry_items WHERE enquiry_id = %s AND deactivated_at IS NULL"
        
        enquiry = self.db_helper.execute_statement(enquiry_sql, (enquiry_id,))
        items = self.db_helper.execute_statement(items_sql, (enquiry_id,))
        
        return (enquiry[0], items) if enquiry else (None, [])

    def update_status(self, enquiry_id, status):
        sql = "UPDATE enquiries SET status = %s WHERE id = %s"
        self.db_helper.execute_command(sql, (status, enquiry_id))

    def get_accepted_enquiries_for_customer(self, customer_id):
        sql = """
            SELECT ei.*, e.enq_number
            FROM enquiry_items ei
            JOIN enquiries e ON ei.enquiry_id = e.id
            WHERE e.customer_id = %s AND e.status = 'accepted' AND e.deactivated_at IS NULL
            AND ei.deactivated_at IS NULL
            AND ei.id NOT IN (SELECT enquiry_item_id FROM order_items WHERE enquiry_item_id IS NOT NULL AND deactivated_at IS NULL)
        """
        return self.db_helper.execute_statement(sql, (customer_id,))

    def delete(self, enquiry_id):
        sql = "UPDATE enquiries SET deactivated_at = %s WHERE id = %s"
        self.db_helper.execute_command(sql, (datetime.now(), enquiry_id))
        
        
    def get_deactivated(self):
        sql = """
            SELECT e.id, e.enq_number, e.status, c.name as customer_name, e.deactivated_at
            FROM enquiries e
            LEFT JOIN customers c ON e.customer_id = c.id
            WHERE e.deactivated_at IS NOT NULL
            ORDER BY e.deactivated_at DESC
        """
        return self.db_helper.execute_statement(sql)