# config.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    # host: str = os.getenv("DB_HOST")
    # port: int = int(os.getenv("DB_PORT", 5432))
    # database: str = os.getenv("DB_NAME")
    # user: str = os.getenv("DB_USER")
    # password: str = os.getenv("DB_PASSWORD")
    host: str = "localhost"
    port: int = 5432
    database: str = "epr"
    user: str = "postgres"
    password: str = "12345678"

    def __post_init__(self):
        print(f"DEBUG: Config initialized with host={self.host}, port={self.port}, database={self.database}, user={self.user}")


