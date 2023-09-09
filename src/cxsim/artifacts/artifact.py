from abc import ABC, abstractmethod
from pydantic import BaseModel
from dataclasses import is_dataclass
from typing import Union
import dataclasses


def generate_prompt(cls: Union[BaseModel, object]):
    if issubclass(cls, BaseModel):
        fields = cls.model_fields
        field_strs = ", ".join([f'"{field_name}": {field.annotation}' for field_name, field in fields.items()])
        method_str = f'{{"action": "{cls.__name__}", "action_parameters": {{{field_strs}}}}}'
    elif is_dataclass(cls):
        cls_fields = dataclasses.fields(cls)
        field_strs = ", ".join([f'"{field.name}": {field.type.__name__}' for field in cls_fields])
        method_str = f'{{"action": "{cls.__name__}", "action_parameters": {{{field_strs}}}}}'
    else:
        raise ValueError("Unsupported class type. Expected a Pydantic BaseModel or a dataclass.")

    return method_str


class Artifact:
    """
    Represents an artifact in the simulation environment, providing interfaces for actions, queries,
    and interactions with agents.

    Attributes:
        name (str): Name of the artifact.
        system_prompt (str): System prompt or message related to the artifact.
        action_space_prompt (str): Prompt for available actions on the artifact.
        event_history (list): Record of past events or interactions with the artifact.
        environment: Reference to the environment in which the artifact exists.
        agents: Reference to agents that can interact with the artifact.
        action_space (list): List of available actions that can be performed on the artifact.
        query_space (list): List of available queries related to the artifact.
    """
    def __init__(self, name):
        """
        Initialize an artifact with a given name.

        :param name: Name of the artifact.
        """
        self.name = name
        self.system_prompt = ""

        self.action_space_prompt = ""
        self.event_history = []

        self.environment = None
        self.agents = None

        self.action_space = []
        self.query_space = []

    @abstractmethod
    def set_up(self, environment):
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
    def process_query(self, agent, query):
        """
        Process a query made by an agent related to the artifact.
        This method should be implemented by subclasses.

        :param agent: Agent making the query.
        :param query: Query to be processed.
        """
        pass

    @abstractmethod
    def step(self):
        """
        Execute a step or update for the artifact.
        This method should be implemented by subclasses.
        """
        pass

    def should_continue(self):
        """
        Determine if the simulation or interaction with the artifact should continue.

        :return: True if the interaction should continue, False otherwise.
        """
        return True

    @abstractmethod
    def get_action_space(self):
        """
        Retrieve the available actions for the artifact.

        :return: List of available actions.
        """
        return self.action_space

    def get_action_space_prompt(self):
        return [generate_prompt(action) for action in self.action_space]

    @abstractmethod
    def get_query_space(self):
        """
        Retrieve the available queries related to the artifact.

        :return: List of available queries.
        """
        return self.query_space

    def get_query_space_prompt(self):
        return [generate_prompt(query) for query in self.query_space]

    @abstractmethod
    def reset(self, environment):
        pass
