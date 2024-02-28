import os
import sqlite3

from cxsim.environment.database.cx_table import CxTable  # Ensure CxTable is correctly imported
from cxsim.environment.database.default_tables import DEFAULT_TABLES


DBMS = [
    "",
]


class CxDatabase:
    def __init__(self, db_name: str = "CxDatabase", extension: str = ".db", directory: str = ""):
        self.db_name = db_name + extension
        self.directory = directory  # Directory where the database file is stored
        # Use os.path.abspath to get the absolute path
        self.file_path = os.path.abspath(os.path.join(self.directory, self.db_name))
        self.conn = None
        self.cursor = None
        self.tables = {}

        self.connect()
        CxTable.db = self
        self.close()

    def manage_table(self, table: CxTable):
        """
        Helper function to drop and recreate tables.
        This can be adjusted or removed based on your actual application needs.
        """
        table.drop()
        table.create()

    def connect(self):
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._set_up_tables()

    def _set_up_tables(self):
        # Recreate tables from DEFAULT_TABLES
        for table_cls in DEFAULT_TABLES:
            t = table_cls()
            t.db = self
            self.manage_table(t)
            self.tables[t.table_name] = t

    def __getitem__(self, table_name: str):
        table = self.tables.get(table_name.lower())
        if table is None:
            raise KeyError(f"Table '{table_name}' not found in the database.")
        return table

    def close(self):
        if self.conn:
            self.conn.close()

    def reset(self):
        # Drop all existing tables
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        for (table_name,) in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

        # Commit changes
        self.conn.commit()

        self._set_up_tables()



