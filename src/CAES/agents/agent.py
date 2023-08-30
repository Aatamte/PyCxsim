import random
from copy import deepcopy
from src.CAES.actions.action_restrictions import ActionRestriction
from src.CAES.agents.item import Item

from src.CAES.agents.tools.tool import Tool

from src.CAES.agents.features.memory.long_term_memory import LongTermMemory

from src.CAES.agents.tools.knowledge_base import KnowledgeBase
from src.CAES.agents.tools.journal import Journal
from src.CAES.agents.features.inventory import Inventory


class Agent:
    """
    Agent represents the lowest-level abstraction in Agent Based Modeling (ABM)

    :param name: name of the agent
    """
    def __init__(self, name: str = "default"):
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

        # agent tools
        self.tools = {}

    def add_tool(self, tool: Tool):
        if tool.name in self.tools:
            raise KeyError("Tool is already in the agent")
        else:
            self.tools[tool.name] = tool

    def execute_action(self):
        raise NotImplementedError("This method should be implemented by subclasses")

    def execute_query(self):
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
