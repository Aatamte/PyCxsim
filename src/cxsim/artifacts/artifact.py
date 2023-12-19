from abc import abstractmethod
from dataclasses import is_dataclass
from typing import Union
import dataclasses
from dataclasses import fields


def generate_prompt(cls: Union[object]):
    if is_dataclass(cls):
        cls_fields = dataclasses.fields(cls)
        field_strs = ", ".join([f'"{field.name}": {field.type.__name__}' for field in cls_fields])
        method_str = f'{{"action": "{cls.__name__}", "action_parameters": {{{field_strs}}}}}'
    else:
        raise ValueError("Unsupported class type. Expected a dataclass.")

    return method_str


class Artifact:
    """
    Represents an artifact in the simulation environment, providing interfaces for actions, queries,
    and interactions with agents.

    Attributes:
        name (str): Name of the artifact.
        event_history (list): Record of past events or interactions with the artifact.
        environment: Reference to the environment in which the artifact exists.
        agents: Reference to agents that can interact with the artifact.
        action_space (list): List of available actions that can be performed on the artifact.
    """
    def __init__(self, name):
        """
        Initialize an artifact with a given name.

        :param name: Name of the artifact.
        """
        self.name = name
        self.event_history = []

        self.environment = None
        self.agents = None

        self.action_space = []

    @abstractmethod
    def compile(self, environment):
        """
        Set up the artifact within a given environment.
        This method should be implemented by subclasses.

        :param environment: The environment in which the artifact exists.
        """
        pass

    @abstractmethod
    def process_action(self, agent, action):
        """
        Process an action performed by an agent on the artifact.
        This method should be implemented by subclasses.

        :param agent: Agent performing the action.
        :param action: Action to be processed.
        """
        pass

    @abstractmethod
    def step(self):
        """
        Execute a step or update for the artifact.
        This method should be implemented by subclasses.
        """
        pass

    @abstractmethod
    def reset(self, environment):
        pass

    def should_continue(self):
        """
        Determine if the simulation or interaction with the artifact should continue.

        :return: True if the interaction should continue, False otherwise.
        """
        return True

    @property
    def get_action_space(self):
        """
        Retrieve the available actions for the artifact.

        :return: List of available actions.
        """
        return self.action_space

    def to_dict(self):
        return {
            "name": self.name,
            "events": self.event_history
        }

    def get_action_space_prompt(self):
        return [generate_prompt(action) for action in self.action_space]

    def get_description(self):
        description = f"{self.name}\ndescription: {self.__doc__}\n"
        description += "ACTIONS:\n"
        for action in self.action_space:
            action_name = str(action.__name__)
            action_parameters = [f"{field.name} {field.type}" for field in fields(action)]
            description += f" -function {action_name}(" + ", ".join(action_parameters) + ")\n"
            description += f"\tDescription: {action.__doc__}\n"
        return description
