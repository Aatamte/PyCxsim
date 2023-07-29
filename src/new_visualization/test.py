from src.core import Agent, Environment
from src.core import Market
import numpy as np
from src.new_visualization.visualizer import Visualizer
import dearpygui.dearpygui as dpg


class MyAgent(Agent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.starting_capital = 500000
        self.starting_inventory = {
            "socks": 100000
        }
        self.is_buyer = True if np.random.randint(0, 100) > 50 else False
        self.quantity = 1 if self.is_buyer else -1

    def select_action(self):
        if self.is_buyer:
            price = np.random.randint(85, 100)
        else:
            price = np.random.randint(90, 105)
        self.action_queue.append(("Market", ["socks", price, self.quantity]))


if __name__ == '__main__':
    env = Environment(enable_visualization=True)
    market = Market("socks")
    env.add(market)
    env.add([MyAgent() for _ in range(10)])

    env.reset()

    with env:
        while env.is_running():
            print("this will run every frame")
            for step in range(env.max_steps):
                print(env.current_step)
                env.step()

