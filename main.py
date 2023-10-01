import os
import random

import openai

from src.cxsim import Environment
from src.cxsim.artifacts.marketplace import Marketplace
from src.cxsim.agents import Population, OAIAgent
from src.cxsim.prompts.prompt import PromptTemplate
from src.cxsim.econ.curves import Demand, Supply

def main():
    openai.api_key = os.environ["openai_api_key"]

    env = Environment(gui=True)

    total_agents = 20

    supply = Supply(total_agents)
    demand = Demand(total_agents)

    # Define Supply and Demand Functions
    demand.set_function(lambda x: 150 - (1 * x))
    supply.set_function(lambda x: (1 * x) + 140)

    buyer_pop = Population(
        agent=OAIAgent,
        number_of_agents=total_agents,
        system_prompt=PromptTemplate("src/cxsim/prompts/system_prompt.txt"),
        cognitive_prompt=PromptTemplate("src/cxsim/prompts/cognitive_prompt.txt"),
        decision_prompt=PromptTemplate("src/cxsim/prompts/decision_prompt.txt"),
        prompt_arguments={"role": "buyer"},
        agent_params={"goal": "buy shirts from other agents for a price lower than the expected value", "shirts Expected Value": demand.function},
        agent_inventory={"capital": 1000, "shirts": 1}
    )

    seller_pop = Population(
        agent=OAIAgent,
        number_of_agents=total_agents,
        system_prompt=PromptTemplate("src/cxsim/prompts/system_prompt.txt"),
        cognitive_prompt=PromptTemplate("src/cxsim/prompts/cognitive_prompt.txt"),
        decision_prompt=PromptTemplate("src/cxsim/prompts/decision_prompt.txt"),
        prompt_arguments={"role": "seller"},
        agent_params={"goal": "sell shirts in the marketplace for a price higher than the expected value", "shirts Expected Value": supply.function},
        agent_inventory={"capital": 1000, "shirts":  20}
    )

    agents = seller_pop.generate_agents() + buyer_pop.generate_agents()
    random.shuffle(agents)

    env.add(agents)

    env.add(Marketplace())

    env.step_delay = 5

    env.max_episodes = 1
    env.max_steps = 50

    # prepare the environment to be run
    env.prepare()

    for step in env.iter_steps():
        print(step)

        env.step()


if __name__ == '__main__':
    main()
