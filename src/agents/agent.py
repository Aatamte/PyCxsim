from collections import deque
from dataclasses import dataclass
import numpy as np
from typing import Union
from copy import deepcopy


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

        # holds the next action that the agent will take
        self.action_queue = []

        #
        self.params = {}

        # inventory
        if inventory is None:
            self.inventory = {"capital": default_starting_capital}

        self.starting_inventory = self.inventory.copy()

    def reset(self):
        self.inventory = self.starting_inventory

    def update(self, observation):
        # update the state depending on the observation
        self.observations.append(observation)

    def execute_next_action(self):
        action = self.action_queue.pop(0)
        self.observations = []
        return action

    def view_next_action(self):
        return str(self.action_queue[0])

    def view_observation(self):
        return str(self.observations[0])

    def select_action(self):
        pass

    def capital(self):
        return self.inventory["capital"]

    def display_inventory(self):
        return str({key: len(value) for key, value in self.inventory.items()})

    def step(self):
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
