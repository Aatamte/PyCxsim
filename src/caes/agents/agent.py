import random
from copy import deepcopy
from abc import ABC, abstractmethod

from src.caes.actions.action_restrictions import ActionRestriction
from src.caes.agents.item import Item

from src.caes.agents.tools.tool import Tool
from src.caes.agents.traits.memory.long_term_memory import LongTermMemory
from src.caes.agents.tools.knowledge_base import KnowledgeBase
from src.caes.agents.tools.journal import Journal
from src.caes.agents.traits.inventory import Inventory
from src.caes.agents.traits.memory.working_memory import WorkingMemory


class Agent:
    """
    Represents an individual agent in the simulation, encapsulating attributes, behaviors, tools, and interactions.

    Attributes:
        name (str): Name of the agent.
        id (int): Unique identifier for the agent, initialized by the environment class.
        x_pos, y_pos (int): Positional coordinates of the agent.
        color (tuple): RGB color representation of the agent.
        role: Role or type of the agent.
        observations (list): List of observations made by the agent.
        messages (list): Messages received or sent by the agent.
        params (dict): Parameters or settings specific to the agent.
        action_history (list): Record of past actions taken by the agent.
        action_restrictions, query_restrictions (dict): Restrictions on actions and queries.
        action_space, query_space (dict): Available actions and queries for the agent.
        system_prompt (str): Prompt or message from the system.
        inventory (Inventory): Inventory of items held by the agent.
        long_term_memory (LongTermMemory): Long-term memory storage of the agent.
        tools (dict): Tools or utilities available to the agent.
    """
    def __init__(self, name: str = "default"):
        """
        Initialize an agent with a given name and default attributes.

        :param name: Name of the agent.
        """
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

        self.inventory = Inventory()

        # agent traits
        self.long_term_memory = LongTermMemory(100)
        self.working_memory = WorkingMemory(self)

        # agent tools
        self.tools = {}

    def add_tool(self, tool: Tool):
        """
        Add a tool to the agent's collection of tools.

        :param tool: Tool object to be added.
        :raises KeyError: If the tool is already present.
        """
        if tool.name in self.tools:
            raise KeyError("Tool is already in the agent")
        else:
            self.tools[tool.name] = tool

    def add_message(self, role: str, content: str):
        self.messages.append(
            {
                "role": role,
                "content": content
            }
        )

    @abstractmethod
    def execute_action(self):
        """
        Execute an action by the agent.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("This method should be implemented by subclasses")

    @abstractmethod
    def execute_query(self):
        """
        Execute a query and return a random choice from the query space.

        :return: A random query from the query space.
        """
        return random.choice(self.query_space)

    def reset(self):
        self.inventory.reset()

    def get_action_space(self):
        return self.action_space

    def get_query_space(self):
        return self.query_space

    def capital(self):
        return self.inventory["capital"]

    def display_inventory(self):
        return str({key: value for key, value in self.inventory.items()})

    def step(self):
        pass

    def update_inventory(self):
        self.inventory = {key: len(value) for key, value in self.inventory.items()}

    def set_up(self):
        pass

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
            if item.action in self.action_restrictions:
                self.action_restrictions[item.action].append(item.restriction_function)
            else:
                self.action_restrictions[item.action] = [item.restriction_function]

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
        return self.inventory.get_quantity(item)

    def values(self):
        return self.inventory.values()

    def display(self):
        return \
            f"""
-----------------------------
Agent: {self.name} 
capital {self.get_amounts("capital")}
-----------------------------"""
