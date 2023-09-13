import os
import openai

from src.cxsim import Environment
from src.cxsim.agents import Population, OAIAgent
from src.cxsim.artifacts import Marketplace

from src.cxsim.agents.agent import before_turn


class MyAgent(OAIAgent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.inventory.set_starting_inventory(
            {"capital": 1000, "socks": 10, "shirts": 5}
        )

    @before_turn
    def say_hello(self):
        print("hello")


if __name__ == '__main__':
    openai.api_key = os.environ["openai_api_key"]
    print("starting")
    env = Environment(gui=True)

    buyer_population = Population(
        agent=MyAgent(),
        number_of_agents=1
    )

    seller_population = Population(
        agent=MyAgent(),
        number_of_agents=1
    )

    env.add(buyer_population)

    marketplace = Marketplace()
    env.add(marketplace)

    env.step_delay = 5

    env.max_episodes = 1
    env.max_steps = 50

    # prepare the environment to be run
    env.prepare()

    for step in env.iter_steps():
        print(step)
        env.step()

