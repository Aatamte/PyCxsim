import os
import openai

from src.cxsim import Environment
from src.cxsim.agents import Population, OAIAgent
from src.cxsim.artifacts import Marketplace


class MyAgent(OAIAgent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.inventory.set_starting_inventory(
            {"capital": 1000, "socks": 10, "shirts": 5}
        )

        self.params["max_price"] = 10


if __name__ == '__main__':
    openai.api_key = os.environ["open_ai_key"]

    env = Environment(gui=True)
    d = 0
    buyer_population = Population(
        agent=MyAgent(),
        number_of_agents=5
    )

    seller_population = Population(
        agent=MyAgent(),
        number_of_agents=5
    )

    env.add(buyer_population)
    env.add(seller_population)

    marketplace = Marketplace()
    env.add(marketplace)

    env.step_delay = 5

    env.max_episodes = 1
    env.max_steps = 50

    # set up the environment
    env.set_up()

    for step in env.iter_steps():
        print(step)
        env.step()

