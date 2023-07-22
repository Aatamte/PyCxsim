import pickle


class BaseAgent:
    def __init__(self, name: str = "default"):
        self.name = name
        self.id = None
        # location information

        # for environment and rendering
        self.num_steps = 0

        # for the environment
        self.xp = 0
        self.xps = [0]
        self.inventory = Inventory(self)
        self.state_space = None
        self.logger = None

    def reset(self):
        self.num_steps = 0
        self.xp = 0

        self.xps.clear()
        self.xps = [0]
        self.inventory.reset()

    def get_reward(self):
        return self.xps[-1] - self.xps[-2]

    def step(self):
        self.inventory.step()
        self.xps.append(sum(self.inventory.values()))
        self.num_steps += 1

    def save(self, path = None):
        if path:
            pickle.dump()
        else:
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
