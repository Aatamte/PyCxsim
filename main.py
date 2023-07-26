from src.core import Agent, Environment
from src.core import Marketplace


class MyAgent(Agent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.inventory.starting_capital = 1000

    def select_action(self):
        return self, "MarketPlace", ["socks", 100, 1]


if __name__ == '__main__':
    env = Environment()
    agent = MyAgent()

    marketplace_artifact = Marketplace(["socks", "bananas"])
    env.add(marketplace_artifact)

    max_episodes = 10
    max_steps = 2

    env.add(agent)

    env.reset()
    for step in range(max_steps):
        actions = [agent.select_action()]
        env.step(actions)
        #print(env)


