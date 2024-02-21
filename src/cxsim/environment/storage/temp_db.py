import sqlite3


class TemporaryDatabase:
    def __init__(self):
        # Connect to a database in RAM, which is temporary
        self.connection = sqlite3.connect(':memory:')
        self.cursor = self.connection.cursor()

        # Define table schemas in a more structured and Pythonic way
        self.table_schemas = {
            'employees': {
                'id': 'INTEGER PRIMARY KEY',
                'name': 'TEXT NOT NULL',
                'position': 'TEXT NOT NULL'
            }
            # Add more tables here as needed
        }

        # Create the predefined tables
        self.create_tables()

    def create_tables(self):
        """Create tables from the structured schema definitions."""
        for table_name, schema in self.table_schemas.items():
            columns = ', '.join(f"{col_name} {col_type}" for col_name, col_type in schema.items())
            create_stmt = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"
            self.cursor.execute(create_stmt)
        self.connection.commit()

    def insert_data(self, table_name, data):
        """Insert data into the table. 'data' should be a dictionary where keys match the table's column names."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' for _ in data)
        insert_stmt = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
        self.cursor.execute(insert_stmt, tuple(data.values()))
        self.connection.commit()

    def query_data(self, table_name, columns='*'):
        """Query data from the table."""
        query_stmt = f"SELECT {columns} FROM {table_name};"
        self.cursor.execute(query_stmt)
        return self.cursor.fetchall()

    def close(self):
        """Close the database connection."""
        self.connection.close()




