
class Agent:
    """
    Agent represents the lowest-level abstraction in Agent Based Modeling (ABM)

    :param name: name of the agent
    """
    def __init__(
            self, name: str = "default",
            starting_capital: int = 0,
            starting_inventory: dict = None
    ):
        self.name = name
        self.id = None  # None, initialized before the first episode by the environment class
        self.x_pos = None
        self.y_pos = None

        # holds the observations for each artifact
        self.observations = []

        # holds the next action that the agent would take
        self.action_queue = []

        # inventory
        self.starting_capital = starting_capital
        self.starting_inventory = {} if starting_inventory is None else starting_inventory
        self.inventory = {}
        self.capital = None

    def reset(self):
        self.capital = self.starting_capital
        self.inventory.clear()
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
Agent: {self.name} 
capital {self.capital}
{self.inventory}
-----------------------------"""


class Inventory:
    def __init__(self, agent, starting_capital: int = 0, starting_inventory: dict = None):
        self.agent = agent
        self.starting_capital = starting_capital
        self.starting_inventory = starting_inventory
        self.capital = starting_capital
        self.inventory = self.starting_inventory if self.starting_inventory else {}
        self.history = []

    def reset(self):
        self.inventory = self.starting_inventory if self.starting_inventory  else {}
        self.capital = self.starting_capital
        self.history.clear()

    def step(self):
        self.history.append(self.inventory.copy())

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
