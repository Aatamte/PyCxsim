from src.core import Agent, Environment
from src.core import Marketplace, Market, Order
from src.core import Dialogue
import time
import random


class MyAgent(Agent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.inventory.starting_capital = 1000

    def select_action(self):
        actions = [
            ("Market", ["socks", 100, 1]),
            ("Market", ["socks", Order(100, 1, self)]),
            ("Dialogue", ["default", "hello"])  # say hello to the "default agent", dialogue can be used in bartering, etc.
        ]
        action = random.choice(actions)
        self.action_queue.append(action)


def main():
    env = Environment()
    agent = MyAgent()
    agent2 = MyAgent()

    # add a market to the environment
    market = Market("socks")

    # add the ability for agents to speak to each other to the environment through messages
    dialogue = Dialogue()

    things = [agent, agent2, market, dialogue]

    # anything that is an <Agent> or <Artifact> class can be added to the environment
    env.add(things)

    env.max_episodes = 10
    env.max_steps = 10
    start = time.time()

    # Reinforcement learning style

    # or CAS style
    env.run()

    end = time.time()

    print(end - start)


if __name__ == '__main__':
    main()

