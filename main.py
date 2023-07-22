from src.core import BaseAgent, BaseEnvironment
from src.core import Marketplace


class MyAgent(BaseAgent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.inventory.starting_capital = 1000

    def select_action(self):
        return self, "MarketPlace", ["socks", 100, 1]


if __name__ == '__main__':
    env = BaseEnvironment()
    agent = MyAgent()

    marketplace_artifact = Marketplace(["socks", "bananas"])
    env.add(marketplace_artifact)

    max_episodes = 10
    max_steps = 2

    env.populate(agent)

    env.reset()
    for step in range(max_steps):
        actions = [agent.select_action()]
        env.step(actions)
        #print(env)


