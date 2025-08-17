import logging
import boto3
from .connection import Connection
from .config import Config


class RDSHelper:
    def __init__(self):
        # Initialize Config
        self.config = Config()
        # Add Debug Log
        print("DEBUG: Initializing RDSHelper with config:")
        print(f"DEBUG: {self.config}")
        
        self.connection = Connection.getInstance(config=self.config)
        
        
    
    def is_connection_alive(self):
        retry_count = 0
        is_alive =False
        while retry_count < 3:
            try:
                cursor = self.connection.cursor()
                cursor.execute("select 1;", None)
                response = cursor.fetchall()
                logging.info("Connection is alive")
                is_alive = True
                break
            except Exception as ex:
                retry_count +=1
                Connection.delete_instance()
                self.connection = Connection.getInstance(config = self.config)
        return is_alive

    def get_result_set(self, rds_response, column_metadata, log_response=True):
        """
        Return a list of row objects with parameter-value pairs extracted from RDS response.
        """
        column_names_list = [column[0] for column in column_metadata]
        result_set = []
        for row in rds_response:
            # Create row objects by mapping column names to row values
            result_set.append(dict(zip(column_names_list, row)))
        # if log_response:
        #     logging.info(f'Query output converted to dict is: {result_set}')
        return result_set

    def execute_statement(self, sql, sql_parameters=None, cursor=None, log_response=True):
        if sql_parameters is None:
            sql_parameters = {}
        handle_transaction = False if cursor is None else True
        if not cursor:
            cursor = self.connection.cursor()

        if handle_transaction:
            cursor.execute(sql, sql_parameters)
            response = cursor.fetchall()
            column_metadata = cursor.description
            return self.get_result_set(response, column_metadata, log_response=log_response)
        else:
            try:
                cursor.execute(sql, sql_parameters)
                response = cursor.fetchall()
                column_metadata = cursor.description
                self.connection.commit()
                cursor.close()
                return self.get_result_set(response, column_metadata, log_response=log_response)
            except Exception as error:
                self.connection.rollback()
                cursor.close()
                logging.error(f'Error happened while executing the query: {error}')
                raise error

    def execute_command(self, sql, sql_parameters=None, cursor=None):
        if sql_parameters is None:
            sql_parameters = {}
        handle_transaction = False if cursor is None else True
        if not cursor:
            cursor = self.connection.cursor()

        if handle_transaction:
            cursor.execute(sql, sql_parameters)
            return cursor.rowcount
        else:
            try:
                cursor.execute(sql, sql_parameters)
                count = cursor.rowcount
                self.connection.commit()
                cursor.close()
                return count
            except Exception as error:
                self.connection.rollback()
                cursor.close()
                logging.error(f'Error happened while executing the query: {error}')
                raise error

    def transact(self, commands, cursor=None):
        handle_transaction = False if cursor is None else True
        if not cursor:
            cursor = self.connection.cursor()

        if handle_transaction:
            for command in commands:
                params = (command.get('params'))
                cursor.execute(command.get('command'), params)
        else:
            try:
                for command in commands:
                    params = (command.get('params'))
                    cursor.execute(command.get('command'), params)
                self.connection.commit()
                cursor.close()
            except Exception as error:
                self.connection.rollback()
                cursor.close()
                logging.error(f'Error happened while executing the query: {error}')
                raise error

    def execute_command_returning_id(self, sql, sql_parameters=None, cursor=None):
        if sql_parameters is None:
            sql_parameters = {}
        handle_transaction = False if cursor is None else True
        if not cursor:
            cursor = self.connection.cursor()

        if handle_transaction:
            cursor.execute(sql, sql_parameters)
            count = cursor.rowcount
            record_id = cursor.fetchone()[0]
            return count, record_id
        else:
            try:
                cursor.execute(sql, sql_parameters)
                count = cursor.rowcount
                record_id = cursor.fetchone()[0]
                self.connection.commit()
                cursor.close()
                return count, record_id
            except Exception as error:
                self.connection.rollback()
                cursor.close()
                logging.error(f'Error happened while executing the query: {error}')
                raise error

    def execute_describe_log_files(self,from_time):
        log_snapshot = self.client.describe_db_log_files(
            DBInstanceIdentifier = self.config.db_audit_name,
            FileLastWritten = int(from_time)
        )
        return log_snapshot
    
    def execute_download_log_file(self,log_name):
        log_content = self.client.download_db_log_file_portion(
            DBInstanceIdentifier = self.config.db_audit_name,
            LogFileName = log_name,
            )
        return log_content
    
    def copy_from(self, sql, file):
        conn = self.connection
        if conn:
            cursor = conn.cursor()
            try:
                cursor.copy_expert(sql=sql, file=file)
                conn.commit()
                cursor.close()
            except Exception as e:
                logging.error('Error while executing the transaction {}'.format(e))
                conn.rollback()
                cursor.close()
