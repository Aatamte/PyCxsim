from typing import List
import inspect
from dataclasses import dataclass


def do_action(action: str, parameters: List[str]):
    return {"action": action, "parameters": parameters}


class Action:
    def __init__(
            self,
            name: str,
            parameters: dict
    ):
        pass

    def from_dict(self):
        pass

    def from_dataclass(self):
        pass


class ActionRestriction:
    def __init__(
            self,
            action,
            func: callable,
            message_to_agent_on_trigger: str = None,
            inform_agent_and_retry_action: bool = True,
            max_retries: int = 3
    ):
        self.action = action
        self.inform_agent_and_retry = inform_agent_and_retry_action
        self.restriction_function = func
        self.max_retries = max_retries
        self.message_to_agent_on_trigger = message_to_agent_on_trigger

        self.current_retries = 0

    def __repr__(self):
        return str(inspect.getsource(self.restriction_function))


@dataclass
class Skip:
    value: str = "None"


STANDARD_ACTIONS = [
    Skip
]
