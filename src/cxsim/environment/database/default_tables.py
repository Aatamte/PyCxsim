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
    past_actions = CxDataType(list)


class CxLogs(CxTable):
    timestamp = CxDataType(datetime.datetime)
    level = CxDataType(str)
    msg = CxDataType(str)


class CxActions(CxTable):
    step: CxDataType(int)
    agent_name: CxDataType(str)
    action_name: CxDataType(str)
    action_parameters = CxDataType(dict)


# keys
# running_state: 0
class CxSimulationState(CxTable):
    key = CxDataType(str, primary_key=True)
    value = CxDataType(str)


DEFAULT_TABLES = [
    CxMetadata,
    CxAgents,
    CxLogs,
    CxActions,
    CxSimulationState
]
