import os
import openai
import logging

from src.cxsim import Environment
from src.cxsim.agents import Population, OAIAgent
from src.cxsim.artifacts import Marketplace
from src.cxsim.artifacts.gridworld import GridWorld
from src.cxsim.prompts.prompt import InitializationPrompt

class MyAgent(OAIAgent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.inventory.set_starting_inventory(
            {"capital": 10000, "books": 100}
        )


def main():
    openai.api_key = os.environ["openai_api_key"]

    env = Environment(gui=True)

    buyer_population = Population(
        agent=MyAgent,
        number_of_agents=5,
        prompt=InitializationPrompt("src/cxsim/prompts/system_prompt.txt"),
        prompt_arguments={"role": "mover"}
    )

    seller_population = Population(
        agent=MyAgent,
        number_of_agents=5,
        prompt=InitializationPrompt("src/cxsim/prompts/system_prompt.txt"),
        prompt_arguments={"role": "mover"}
    )

    env.add(buyer_population)
    env.add(seller_population)

    #marketplace = Marketplace()
    #env.add(marketplace)

    gridworld = GridWorld()
    env.add(gridworld)

    env.step_delay = 5

    env.max_episodes = 1
    env.max_steps = 10

    env.log(logging.INFO, "The environment is about to be prepared")
    # prepare the environment to be run
    env.prepare()

    for step in env.iter_steps():
        print(step)
        env.step()


if __name__ == '__main__':
    main()
