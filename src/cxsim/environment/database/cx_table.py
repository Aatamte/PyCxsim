import json

from cxsim.environment.database.cx_data_types import CxDataType


class CxTable:
    db = None  # This will be set to the CxDatabase instance

    def __init__(self):
        self.table_name = self.__class__.__name__.lower()  # Infer the table name
        self.columns = {}
        self.primary_keys = []

        self.protected = getattr(self.__class__, '__protected__', False)

        # Extract column definitions and primary key info
        for attr, attr_def in vars(self.__class__).items():
            if isinstance(attr_def, CxDataType):
                self.columns[attr] = attr_def.to_sql()
                if attr_def.primary_key:
                    self.primary_keys.append(attr)

        self.schema = self._generate_schema()

    def _generate_schema(self):
        """Generate the SQL schema statement from class attributes."""
        columns_definitions = [f"{attr} {defn}" for attr, defn in self.columns.items()]
        return ", ".join(columns_definitions)

    def create_table_query(self):
        """Generate the SQL CREATE TABLE statement using instance attributes."""
        columns_definitions = [f"{attr} {defn}" for attr, defn in self.columns.items()]
        columns_sql = ', '.join(columns_definitions)
        return f"CREATE TABLE IF NOT EXISTS {self.table_name} ({columns_sql})"

    def serialize(self, **kwargs):
        """Serialize column-value pairs."""
        serialized = {}
        for attr, value in kwargs.items():
            column_data_type = getattr(self.__class__, attr, None)
            if column_data_type:
                serialized[attr] = column_data_type.serialize(value)
            else:
                serialized[attr] = value
        return serialized

    def deserialize(self, **kwargs):
        """Deserialize column-value pairs."""
        deserialized = {}
        for attr, value in kwargs.items():
            if value is None:
                deserialized[attr] = None
            else:
                column_data_type = getattr(self.__class__, attr, None)
                if column_data_type:
                    deserialized[attr] = column_data_type.deserialize(value)
                else:
                    deserialized[attr] = value
        return deserialized

    @classmethod
    def display(cls):
        """Class method to display the contents of the table."""
        if cls.db and cls.db.conn:
            cursor = cls.db.conn.cursor()
            table_name = cls.__name__.lower()
            cursor.execute(f"SELECT * FROM {table_name}")
            print(cursor.fetchall())
        else:
            print("Database connection is not available.")

    def add(self, **kwargs):
        """
        Add a new entry to the table, with serialization of data.
        :param kwargs: Column-value pairs to be inserted.
        """
        serialized_data = self.serialize(**kwargs)
        columns = ', '.join(serialized_data.keys())
        placeholders = ', '.join(['?' for _ in serialized_data])
        values = tuple(serialized_data.values())

        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        self.execute(query, values)

    def upsert(self, **kwargs):
        """
        Insert a new entry into the table, or update the existing entry if the record already exists,
        based on the primary key columns.
        :param kwargs: Column-value pairs to be inserted or updated.
        """
        serialized_data = self.serialize(**kwargs)
        columns = ', '.join(serialized_data.keys())
        placeholders = ', '.join(['?' for _ in serialized_data])
        update_assignments = ', '.join([f"{col}=excluded.{col}" for col in serialized_data.keys()])
        values = tuple(serialized_data.values())

        # Use self.primary_keys to automatically infer unique columns for conflict resolution
        if not self.primary_keys:
            raise ValueError("No primary keys defined for upsert operation.")

        conflict_columns = ', '.join(self.primary_keys)

        query = f"""
        INSERT INTO {self.table_name} ({columns})
        VALUES ({placeholders})
        ON CONFLICT({conflict_columns}) DO UPDATE SET {update_assignments}
        """
        self.execute(query, values)

    def upsert_many(self, entries):
        """
        Insert multiple entries into the table, or update existing entries if the records already exist,
        based on the primary key columns.
        :param entries: A list of dictionaries representing the entries to be inserted or updated.
        """
        if not entries:
            return

        serialized_entries = [self.serialize(**entry) for entry in entries]
        columns = ', '.join(serialized_entries[0].keys())
        placeholders = ', '.join(['?' for _ in serialized_entries[0]])
        update_assignments = ', '.join([f"{col}=excluded.{col}" for col in serialized_entries[0].keys()])

        if not self.primary_keys:
            raise ValueError("No primary keys defined for upsert_many operation.")

        conflict_columns = ', '.join(self.primary_keys)

        query = f"""
        INSERT INTO {self.table_name} ({columns})
        VALUES ({placeholders})
        ON CONFLICT({conflict_columns}) DO UPDATE SET {update_assignments}
        """

        values = [tuple(entry.values()) for entry in serialized_entries]

        self.execute(query, values, execute_many=True)

    def reset(self):
        """
        Reset the table by deleting all entries.
        """
        if not self.protected:
            query = f"DELETE FROM {self.table_name}"
            self.execute(query)

    def create(self):
        """
        Create the table in the database using the schema defined in the class.
        """
        if not self.protected:
            query = self.create_table_query()  # Use the class method to generate the SQL statement
            self.execute(query)

    def drop(self):
        """
        Drop the table from the database.
        """
        if not self.protected:
            query = f"DROP TABLE IF EXISTS {self.table_name}"
            self.execute(query)

    def execute(self, query, values=None, commit=True, execute_many: bool = False, fetch_result=False):
        """
        Execute a query with optional value parameters and transaction handling.
        :param query: The SQL query to execute.
        :param values: Optional; a tuple of values to be used with the query.
        :param commit: Optional; a boolean indicating whether to commit the transaction (default: True).
        :param fetch_result: Optional; a boolean indicating whether to fetch the result of the query (default: False).
        :return: The result of the query if fetch_result is True, otherwise None.
        """
        cursor = self.db.conn.cursor()
        result = None
        try:
            # Check if there's an active transaction
            active_transaction = self.db.conn.in_transaction

            # Start a new transaction only if there's no active transaction
            if not active_transaction:
                cursor.execute("BEGIN")

            if values:
                if execute_many:
                    cursor.executemany(query, values)
                else:
                    cursor.execute(query, values)
            else:
                cursor.execute(query)

            if fetch_result:
                rows = cursor.fetchall()
                result = [
                    self.deserialize(**dict(zip([col[0] for col in cursor.description], row)))
                    for row in rows
                ]

            if commit and not active_transaction:
                # Check if there's an active transaction before committing
                if self.db.conn.in_transaction:
                    self.db.conn.commit()
        except Exception as e:
            if not active_transaction:
                self.db.conn.rollback()
            raise e
        finally:
            cursor.close()

        return result

    def get(self, **kwargs):
        """
        Retrieve entries from the table. If no arguments are provided, all entries are retrieved.
        :param kwargs: Optional; column-value pairs used for filtering the results.
        """
        if kwargs:
            # Construct the WHERE clause if filtering arguments are provided
            where_clauses = ' AND '.join([f"{column} = ?" for column in kwargs])
            values = tuple(kwargs.values())
            query = f"SELECT * FROM {self.table_name} WHERE {where_clauses}"
        else:
            # Select all records if no arguments are given
            query = f"SELECT * FROM {self.table_name}"
            values = ()

        # Execute the query

        result = self.execute(
            query,
            values,
            fetch_result=True
        )

        return result

    def emit(self, socket):
        """
        Emit the contents of the table to the specified socket.
        :param socket: The socket to emit the data to.
        """
        # Retrieve all entries from the table
        data = self.get()

        # Emit the serialized data to the specified socket
        socket.emit('data_update', {
            'table_name': self.table_name,
            'content': data
        })


