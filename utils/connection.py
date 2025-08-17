# connection.py
import psycopg2
from psycopg2 import OperationalError
from .config import Config

class Connection:
    _instance = None

    @classmethod
    def getInstance(cls, config=None):
        if cls._instance is None:
            try:
                if config is None:
                    raise ValueError("Config object is None.")
                
                # Add Debug Log
                print(f"DEBUG: Attempting connection with host={config.host}, port={config.port}, db={config.database}, user={config.user}")
                
                cls._instance = psycopg2.connect(
                    host=config.host,
                    database=config.database,
                    user=config.user,
                    password=config.password,
                    port=config.port,
                    # sslmode="require"
                )
            except OperationalError as e:
                print(f"Failed to connect to the database: {e}")
                raise
        return cls._instance

    @classmethod
    def delete_instance(cls):
        cls._instance = None


