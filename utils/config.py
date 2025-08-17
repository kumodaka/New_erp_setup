# config.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    host: str = "erp-project.cry06kecilwo.ap-south-1.rds.amazonaws.com"
    port: int = 5432
    database: str = "postgres"
    user: str = "erpAdmin"
    password: str = "eALrFJmSciEMCFa"
    # host: str = "localhost"
    # port: int = 5432
    # database: str = "epr"
    # user: str = "postgres"
    # password: str = "12345678"

    def __post_init__(self):
        print(f"DEBUG: Config initialized with host={self.host}, port={self.port}, database={self.database}, user={self.user}")


