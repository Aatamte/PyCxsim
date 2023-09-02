import os
import openai

from src.CAES import Environment
from src.CAES.agents import Population, OAIAgent
from src.CAES.artifacts import Marketplace


class MyAgent(OAIAgent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.inventory.set_starting_inventory(
            {"capital": 1000, "socks": 10}
        )

        self.params["max_price"] = 10

if __name__ == '__main__':
    openai.api_key = os.environ["open_ai_key"]

    env = Environment(visualization=True)

    buyer_population = Population(
        agent=MyAgent(),
        number_of_agents=2
    )

    seller_population = Population(
        agent=MyAgent(),
        number_of_agents=2
    )

    env.add(buyer_population)
    env.add(seller_population)

    marketplace = Marketplace()
    env.add(marketplace)

    env.step_delay = 2

    env.max_episodes = 1
    env.max_steps = 50

    # set up the environment
    env.set_up()

    for step in env.iter_steps():
        for agent in env.agents:
            print(agent.inventory)
        print(step)
        env.step()

