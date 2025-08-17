# models/invoice.py
from utils.rds_helper import RDSHelper
from datetime import datetime

class Invoice:
    def __init__(self):
        self.db_helper = RDSHelper()

    def get_new_invoice_number(self):
        last_invoice = self.db_helper.execute_statement(
            "SELECT invoice_number FROM invoices ORDER BY id DESC LIMIT 1"
        )
        if not last_invoice:
            return "INV-1"
        
        last_no = int(last_invoice[0]['invoice_number'].split('-')[1])
        return f"INV-{last_no + 1}"

    def create_invoice_with_items(self, data):
        invoice_number = self.get_new_invoice_number()
        
        invoice_sql = """
            INSERT INTO invoices (invoice_number, customer_id, dc_number, dc_date, po_number, po_date, 
            gst_rate, sub_total, gst_amount, total_amount, payment_terms)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """
        
        conn = self.db_helper.connection
        try:
            with conn.cursor() as cur:
                cur.execute(invoice_sql, (
                    invoice_number, data['customer_id'], data['dc_number'], data['dc_date'],
                    data['po_number'], data['po_date'], data['gst_rate'], data['sub_total'],
                    data['gst_amount'], data['total_amount'], data['payment_terms']
                ))
                invoice_id = cur.fetchone()[0]

                item_insert_sql = "INSERT INTO invoice_items (invoice_id, order_item_id, work_order_number, hsn_number) VALUES (%s, %s, %s, %s)"
                for item in data['items']:
                    cur.execute(item_insert_sql, (
                        invoice_id, item['order_item_id'], item['work_order_number'], item['hsn_number']
                    ))

            conn.commit()
            return invoice_id
        except Exception as e:
            conn.rollback()
            raise e

    def get_all(self):
        sql = """
            SELECT i.id, i.invoice_number, i.total_amount, i.payment_terms, c.name as customer_name, i.created_at
            FROM invoices i
            JOIN customers c ON i.customer_id = c.id
            WHERE i.deactivated_at IS NULL
            ORDER BY i.created_at DESC
        """
        return self.db_helper.execute_statement(sql)

    def get_details_by_id(self, invoice_id):
        invoice_sql = "SELECT i.*, c.name as customer_name, c.gst_no, c.address FROM invoices i JOIN customers c ON i.customer_id = c.id WHERE i.id = %s"
        items_sql = """
            SELECT ii.hsn_number, oi.part_number, oi.drawing_number, oi.quantity, oi.unit_price, oi.total_price
            FROM invoice_items ii
            JOIN order_items oi ON ii.order_item_id = oi.id
            WHERE ii.invoice_id = %s
        """
        invoice = self.db_helper.execute_statement(invoice_sql, (invoice_id,))
        items = self.db_helper.execute_statement(items_sql, (invoice_id,))
        return (invoice[0], items) if invoice else (None, [])