# models/user.py
from utils.rds_helper import RDSHelper
from werkzeug.security import generate_password_hash

class User:
    def __init__(self):
        self.db_helper = RDSHelper()

    def create(self, username, password):
        password_hash = generate_password_hash(password)
        sql = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
        self.db_helper.execute_command(sql, (username, password_hash))

    def find_by_username(self, username):
        sql = "SELECT * FROM users WHERE username = %s"
        result = self.db_helper.execute_statement(sql, (username,))
        return result[0] if result else None