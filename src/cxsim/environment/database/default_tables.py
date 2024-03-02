import datetime

from cxsim.environment.database.cx_table import CxTable
from cxsim.environment.database.cx_data_types import CxDataType


class CxMetadata(CxTable):
    key = CxDataType(str, primary_key=True)
    value = CxDataType(str)


class CxAgents(CxTable):
    name = CxDataType(str, primary_key=True)

    x_pos = CxDataType(int)
    y_pos = CxDataType(int)

    parameters = CxDataType(dict)
    inventory = CxDataType(dict)
    messages = CxDataType(list)


class CxLogs(CxTable):
    timestamp = CxDataType(datetime.datetime)
    level = CxDataType(str)
    msg = CxDataType(str)


DEFAULT_TABLES = [
    CxMetadata,
    CxAgents,
    CxLogs,
]
