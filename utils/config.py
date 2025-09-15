# config.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    host: str = "kumodak-db-kumodaka.k.aivencloud.com"
    port: int = 21498
    database: str = "defaultdb"
    user: str = "avnadmin"
    password: str = "AVNS_GwCqNuobXPANnp-_-Hc"
    # host: str = "localhost"
    # port: int = 5432
    # database: str = "epr"
    # user: str = "postgres"
    # password: str = "12345678"

    def __post_init__(self):
        print(f"DEBUG: Config initialized with host={self.host}, port={self.port}, database={self.database}, user={self.user}")


