# models/customer.py
from utils.rds_helper import RDSHelper
from datetime import datetime

class Customer:
    def __init__(self):
        self.db_helper = RDSHelper()

    def get_new_unique_no(self):
        last_customer = self.db_helper.execute_statement(
            "SELECT unique_no FROM customers ORDER BY id DESC LIMIT 1"
        )
        if not last_customer:
            return "AWN-1"
        
        last_no = int(last_customer[0]['unique_no'].split('-')[1])
        return f"AWN-{last_no + 1}"

    def create(self, name, address, phone, gst, pan):
        unique_no = self.get_new_unique_no()
        sql = """
            INSERT INTO customers (unique_no, name, address, phone_number, gst_no, pan_no)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.db_helper.execute_command(sql, (unique_no, name, address, phone, gst, pan))

    def get_all(self):
        return self.db_helper.execute_statement(
            "SELECT * FROM customers WHERE deactivated_at IS NULL ORDER BY id DESC"
        )

    def get_by_id(self, customer_id):
        result = self.db_helper.execute_statement(
            "SELECT * FROM customers WHERE id = %s AND deactivated_at IS NULL", (customer_id,)
        )
        return result[0] if result else None

    def update(self, customer_id, name, address, phone, gst, pan):
        sql = """
            UPDATE customers SET name=%s, address=%s, phone_number=%s, gst_no=%s, pan_no=%s
            WHERE id = %s
        """
        self.db_helper.execute_command(sql, (name, address, phone, gst, pan, customer_id))

    def delete(self, customer_id):
        sql = "UPDATE customers SET deactivated_at = %s WHERE id = %s"
        self.db_helper.execute_command(sql, (datetime.now(), customer_id))
        
    def get_deactivated(self):
        return self.db_helper.execute_statement(
            "SELECT * FROM customers WHERE deactivated_at IS NOT NULL ORDER BY deactivated_at DESC"
        )