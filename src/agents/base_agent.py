import pickle


class Agent:
    def __init__(self, name: str = "default"):
        self.name = name
        self.id = None
        self.observations = []
        self.action_queue = []

        # for environment and rendering
        self.current_step = 0

        # for the environment
        self.inventory = Inventory(self)
        self.logger = None

    def reset(self):
        self.inventory.reset()

    def step(self):
        self.inventory.step()

    def update(self, observation):
        # update the state depending on the observation
        self.observations.append(observation)

    def execute_next_action(self):
        action = self.action_queue.pop(0)
        return action

    def view_next_action(self):
        return str(self.action_queue[0])

    def view_observation(self):
        return str(self.observations)

    def select_action(self):
        pass

    @property
    def capital(self):
        return self.inventory["capital"]


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
