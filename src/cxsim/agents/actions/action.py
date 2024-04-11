from typing import List
import inspect
from dataclasses import dataclass


def do_action(action: str, parameters: List[str]):
    return {"action": action, "parameters": parameters}


class Action:
    """Base class for actions. Utilizes class introspection to provide common functionality."""

    def __init__(self, **kwargs):
        # Store original parameters for use in to_dict, __repr__, and __str__
        # Made truly private to prevent accidental external access
        self.__params = kwargs
        for attr_name, attr_value in kwargs.items():
            # Only set an attribute if it's already defined in the class
            if hasattr(self, attr_name):
                setattr(self, attr_name, attr_value)
            else:
                raise AttributeError(f"'{attr_name}' is not a valid attribute of '{self.__class__.__name__}'")

    def _get_params(self):
        # Safely access the stored parameters
        return self.__params

    def to_dict(self):
        # Exclude '__params' and other built-in or callable attributes from the output
        parameters = {attr_name: getattr(self, attr_name) for attr_name in dir(self)
                      if not attr_name.startswith("__") and not callable(getattr(self, attr_name))
                      and attr_name not in ['__dict__', '__weakref__', '_Action__params']}
        return {'name': self.__class__.__name__, 'parameters': parameters}

    def __repr__(self):
        params_repr = ', '.join(f"{key}={repr(value)}" for key, value in self._get_params().items())
        return f"{self.__class__.__name__}({params_repr})"

    def __str__(self):
        params_str = ', '.join(f"{key}={value}" for key, value in self._get_params().items())
        return f"{self.__class__.__name__}({params_str})"

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
