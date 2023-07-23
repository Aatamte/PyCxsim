from src.core import Agent, Environment
from src.core import Marketplace


class MyAgent(Agent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.inventory.starting_capital = 1000

    def select_action(self):
        self.action_queue.append(("Marketplace", ["socks", 100, 1]))


if __name__ == '__main__':
    env = Environment()
    agent = MyAgent()

    marketplace_artifact = Marketplace(["socks", "bananas"])
    env.add(marketplace_artifact)
    env.add(agent)

    env.max_episodes = 10
    env.max_steps = 2

    env.reset()
    for step in range(env.max_steps):
        agent.select_action()
        #print(agent.view_next_action())
        env.step()  # executing next action and gives agents the
        observation = agent.view_observation()
        print(observation)


