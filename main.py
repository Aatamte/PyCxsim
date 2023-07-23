from src.core import Agent, Environment
from src.core import Marketplace, Market
from src.core import Dialogue
import time
import random


class MyAgent(Agent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.inventory.starting_capital = 1000

    def select_action(self):
        actions = [("Market", ["socks", 100, 1]), ("Dialogue", ["default", "hello"])]
        action = random.choice(actions)
        self.action_queue.append(action)


if __name__ == '__main__':
    env = Environment()
    agent = MyAgent()
    agent2 = MyAgent()

    market_artifact = Market("socks")
    dialogue = Dialogue()

    env.add(market_artifact)
    env.add(dialogue)
    env.add(agent)

    env.max_episodes = 10
    env.max_steps = 10
    start = time.time()
    env.reset()
    for step in range(env.max_steps):
        agent.select_action()
        env.step()  # executing next action and gives agents the
        observation = agent.view_observation()
        print(observation)


    end = time.time()
    print(end - start)
