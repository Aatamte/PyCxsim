import datetime
import json


class CxDataType:
    type_mapping = {
        int: "INTEGER",
        str: "TEXT",
        float: "REAL",
        bytes: "BLOB",  # Added BLOB data type
        datetime.datetime: "TIMESTAMP",  # Added TIMESTAMP data type
        datetime.date: "DATE",  # Added DATE data type
        # Added JSON data type
        dict: "JSON",
        list: "JSON",
        tuple: "JSON"
    }

    def __init__(self, data_type, primary_key=False, unique=False, not_null=False, default=None, check=None):
        self.data_type = data_type
        self.primary_key = primary_key
        self.unique = unique
        self.not_null = not_null
        self.default = default
        self.check = check

    def to_sql(self):
        """Map Python types to SQL types with primary key option."""
        sql_type = self.type_mapping.get(self.data_type, "TEXT")
        if self.primary_key:
            sql_type += " PRIMARY KEY"
        if self.unique and not self.primary_key:
            sql_type += " UNIQUE"
        if self.not_null:
            sql_type += " NOT NULL"
        if self.default is not None:
            default_value = f"'{self.default}'" if isinstance(self.default, str) else self.default
            sql_type += f" DEFAULT {default_value}"
        if self.check is not None:
            sql_type += f" CHECK ({self.check})"
        return sql_type

    def serialize(self, value):
        """Serialize a Python value to its database representation."""
        if self.data_type in (dict, list, tuple):
            return json.dumps(value)
        elif self.data_type == datetime.datetime:
            return value.isoformat()
        elif self.data_type == datetime.date:
            return value.isoformat()
        else:
            return value

    def deserialize(self, value):
        """Deserialize a database value to its Python representation."""
        if self.data_type in (dict, list, tuple):
            return json.loads(value)
        elif self.data_type == datetime.datetime:
            return str(datetime.datetime.fromisoformat(value))
        elif self.data_type == datetime.date:
            return  str(datetime.date.fromisoformat(value))
        else:
            return value
