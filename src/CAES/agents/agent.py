from copy import deepcopy
from src.CAES.actions.action_restrictions import ActionRestriction
from src.CAES.agents.inventory import Inventory
from src.CAES.agents.item import Item


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

    def execute_action(self):
        raise NotImplementedError("This method should be implemented by subclasses")

    def execute_query(self):
        raise NotImplementedError("This method should be implemented by subclasses")

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

    def trade(self, this_agents_item: tuple, other_agents_item: tuple, other_agent):
        # Extract item details
        this_item_name, this_item_price = this_agents_item
        other_item_name, other_item_price = other_agents_item

        # If this agent is trading an item for capital
        if other_item_name == "capital":
            total_cost = this_item_price * this_item_price  # Price per item multiplied by itself

            # Transfer the capital from the other agent to this agent
            for _ in range(total_cost):
                single_capital_unit = other_agent.capital().pop(0)
                self.inventory["capital"].append(single_capital_unit)

            # Transfer a single item from this agent to the other agent
            single_item = self.inventory[this_item_name].pop(0)
            other_agent.__iadd__(single_item)

        # If the other agent is trading an item for capital
        elif this_item_name == "capital":
            total_cost = other_item_price * other_item_price  # Price per item multiplied by itself

            # Transfer the capital from this agent to the other agent
            for _ in range(total_cost):
                single_capital_unit = self.capital().pop(0)
                other_agent.inventory["capital"].append(single_capital_unit)

            # Transfer a single item from the other agent to this agent
            single_item = other_agent.inventory[other_item_name].pop(0)
            self.__iadd__(single_item)

        # Handle non-capital trades
        else:
            for _ in range(this_item_price):
                single_item = self.inventory[this_item_name].pop(0)
                other_agent.__iadd__(single_item)
            for _ in range(other_item_price):
                single_item = other_agent.inventory[other_item_name].pop(0)
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
