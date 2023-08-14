from src.core import Agent, Environment
from src.core import Market, Order, Dialogue, Marketplace
from src.agents.language_model_agents.openai_agent import OAIAgent
from src.agents.population import Population
import numpy as np


class MyAgent(Agent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.starting_inventory = {
            "capital": 10000,
            "socks": 100
        }

    def select_action(self):
        if self.params["is_buyer"]:
            quantity = 1
            price = np.random.randint(85, 100)
        else:
            quantity = -1
            price = np.random.randint(90, 105)

        if np.random.randint(0, 100) > 50:
            self.action_queue.append((Order(good="socks", price=price, quantity=quantity, agent=self)))
        else:
            self.action_queue.append(None)


if __name__ == '__main__':
    env = Environment(enable_visualization=True)

    buyer_params = {"is_buyer": True}

    seller_params = {"is_buyer": False}

    buyer_population = Population(MyAgent(), 2, buyer_params)
    env.add(buyer_population)

    seller_population = Population(MyAgent(), 10, seller_params)
    env.add(seller_population)

    marketplace = Marketplace()

    env.add(marketplace)

    env.add(Dialogue())

    env.step_delay = 1

    env.max_episodes = 100000
    env.max_steps = 100000

    # set up the environment
    env.set_up()

    while env.is_running():
        for step in env.iter_steps():
            current_episode = env.current_episode
            env.step()
