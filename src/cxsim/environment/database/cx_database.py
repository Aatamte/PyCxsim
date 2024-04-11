import os
import sqlite3
from typing import Dict, Type, Optional

from cxsim.environment.database.cx_table import CxTable  # Ensure CxTable is correctly imported
from cxsim.environment.database.default_tables import DEFAULT_TABLES


class CxDatabase:
    def __init__(self, db_name: str = "CxDatabase", extension: str = ".db", directory: str = "") -> None:
        self.db_name: str = db_name + extension
        self.directory: str = directory  # Directory where the database file is stored
        self.file_path: str = os.path.abspath(os.path.join(self.directory, self.db_name))
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.tables: Dict[str, CxTable] = {}  # Assuming CxTable has a 'table_name' attribute

        self.connect()
        CxTable.db = self  # Assuming CxTable has a 'db' class attribute that needs to be set
        self.close()

    def connect(self) -> None:
        self.conn = sqlite3.connect(self.file_path, check_same_thread=False)  # Changed to use file_path instead of db_name
        self.cursor = self.conn.cursor()

    def add(self, table: CxTable):
        """Adds a CxTable to the database and registers it.

        Args:
            table (CxTable): The table to add to the database.

        Raises:
            ValueError: If a table with the same name already exists in the database.
        """
        t: CxTable = table()  # Assuming table_cls() returns an instance of CxTable
        if t.table_name in self.tables:
            # Here, you could also choose to overwrite or just return if the table exists
            raise ValueError(f"Table '{t.table_name}' already exists in the database.")

        t.db = self
        t.drop()  # Assuming CxTable has a drop method
        t.create()  # Assuming CxTable has a create method
        self.tables[t.table_name] = t  # Assuming CxTable instances have a 'table_name' attribute

    def _set_up_default_tables(self) -> None:
        for table_cls in DEFAULT_TABLES:
            self.add(table_cls)

    def __getitem__(self, table_name: str) -> CxTable:
        table = self.tables.get(table_name.lower())
        if table is None:
            raise KeyError(f"Table '{table_name}' not found in the database.")
        return table

    def close(self) -> None:
        if self.conn:
            self.conn.close()

    def reset(self) -> None:
        # Drop all existing tables
        assert self.cursor is not None, "Database must be connected to reset."
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        for (table_name,) in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

        # Commit changes
        assert self.conn is not None, "Database must be connected to commit."
        self.conn.commit()

        self._set_up_default_tables()



