from collections import deque
from dataclasses import dataclass
import numpy as np
from typing import Union
from copy import deepcopy
import inspect


@dataclass
class Item:
    name: str
    uid: Union[np.uint, int]


@dataclass
class Trade:
    item_one: Item
    item_two: Item


def pre_process_action(pre_process_func):
    def decorator(select_action_func):
        def wrapper(self, *args, **kwargs):
            pre_process_func(self, *args, **kwargs)
            return select_action_func(self, *args, **kwargs)
        return wrapper
    return decorator


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


class Agent:
    """
    Agent represents the lowest-level abstraction in Agent Based Modeling (ABM)

    :param name: name of the agent
    """
    def __init__(
            self, name: str = "default",
            inventory: dict = None,
            default_starting_capital: int = 50
    ):
        self.name = name
        self.id = None  # None, initialized before the first episode by the environment class
        self.x_pos = None
        self.y_pos = None
        self.color: tuple = (0, 0, 0)
        self.role = None

        # holds the observations for each artifact
        self.observations = []

        # holds messages
        self.messages = []

        # holds agent parameters
        self.params = {}

        # records past actions
        self.action_history = []

        # action restrictions
        self.action_restrictions = {}

        # query restrictions
        self.query_restrictions = {}

        # action space
        self.action_space = {}

        # query space
        self.query_space = {}

        self.system_prompt = ""

        # inventory
        if inventory is None:
            self.inventory = {"capital": default_starting_capital}

        self.starting_inventory = self.inventory.copy()

    def execute_action(self):
        raise NotImplementedError("This method should be implemented by subclasses")

    def execute_query(self):
        raise NotImplementedError("This method should be implemented by subclasses")

    def reset(self):
        self.inventory = self.starting_inventory

    def get_action_space(self):
        return self.action_space

    def get_query_space(self):
        return self.query_space

    def capital(self):
        return self.inventory["capital"]

    def display_inventory(self):
        return str({key: len(value) for key, value in self.inventory.items()})

    def step(self):
        pass

    def set_up(self):
        pass

    def trade(self, this_agents_item: tuple, other_agents_item: tuple, other_agent):

        # transfer agent two's item
        for amount in range(this_agents_item[1]):
            single_item = self.inventory[this_agents_item[0]].pop()
            other_agent += single_item

        for amount in range(other_agents_item[1]):
            single_item = other_agent.inventory[other_agents_item[0]].pop()
            self.__iadd__(single_item)

    def __isub__(self, other):
        if not isinstance(other, Item):
            raise Warning("Can only add an Item class to the Agent")
        elif other.name in self.inventory.keys():
            self.inventory[other.name].append(other)
            return self
        else:
            pass

    def add(self, item):
        if isinstance(item, ActionRestriction):
            self.action_restrictions.append()

    def __iadd__(self, other: Item):
        if not isinstance(other, Item):
            raise Warning("Can only add an Item class to the Agent")
        elif other.name in self.inventory.keys():
            self.inventory[other.name].append(other)
            return self
        else:
            pass

    def copy(self):
        return deepcopy(self)

    def __getitem__(self, item):
        if item in self.inventory.keys():
            return self.inventory[item]

        # if item does not exist, assume they 0 of it
        return 0

    def __repr__(self):
        return str(self.name)

    def __setitem__(self, key, value):
        if key == "capital":
            self.capital = value
        elif key in self.inventory.keys():
            self.inventory[key] = value
        else:
            self.inventory[key] = value

    def get_amounts(self, item):
        if item in self.inventory.keys():
            if isinstance(self.inventory[item], int):
                return "unverified " + str(self.inventory[item])
            return len(self.inventory[item])
        else:
            return 0

    def values(self):
        return self.inventory.values()

    def display(self):
        return \
            f"""
-----------------------------
Agent: {self.name} 
capital {self.get_amounts("capital")}
-----------------------------"""

class Inventory:
    def __init__(self, agent, starting_capital: int = 0, starting_inventory: dict = None):
        self.agent = agent
        self.starting_capital = starting_capital
        self.starting_inventory = starting_inventory
        self.capital = starting_capital
        self.inventory = self.starting_inventory if self.starting_inventory else {}

    def reset(self):
        self.inventory = self.starting_inventory if self.starting_inventory  else {}
        self.capital = self.starting_capital

    def step(self):
        pass

    def __getitem__(self, item):
        if item in self.inventory.keys():
            return self.inventory[item]

        # if item does not exist, assume they 0 of it
        return 0

    def __setitem__(self, key, value):
        if key == "capital":
            self.capital = value
        elif key in self.inventory.keys():
            self.inventory[key] = value
        else:
            self.inventory[key] = value

    def values(self):
        return self.inventory.values()

    def __repr__(self):
        return \
f"""
-----------------------------
Agent: {self.agent.name} 
capital {self.capital}
{self.inventory}
-----------------------------"""
