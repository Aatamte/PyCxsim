from src.core import Agent, Environment
from src.core import Market, Order, Dialogue, Marketplace
import numpy as np


class MyAgent(Agent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.starting_inventory = {"capital": 10000, "socks": 100}
        self.is_buyer = True if np.random.randint(0, 100) > 50 else False
        self.quantity = 1 if self.is_buyer else -1

    def select_action(self):
        if self.is_buyer:
            price = np.random.randint(85, 100)
        else:
            price = np.random.randint(90, 105)

        if np.random.randint(0, 100) > 50:
            self.action_queue.append((Order(good="socks", price=price, quantity=self.quantity, agent=self)))
        else:
            self.action_queue.append(None)


if __name__ == '__main__':
    env = Environment(enable_visualization=True)
    env.add([MyAgent() for _ in range(20)])

    marketplace = Marketplace()
    env.add(marketplace)

    env.add(Dialogue())

    env.step_delay = 1

    env.max_episodes = 100000
    env.max_steps = 100000

    env.reset()

    while env.is_running():
        for step in env.iter_steps():
            current_episode = env.current_episode
            env.step()
