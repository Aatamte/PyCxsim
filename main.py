import random

from src.cxsim import Environment
from src.cxsim.artifacts.marketplace import Marketplace
from src.cxsim.agents import Population, OpenAIAgent
from src.cxsim.prompts.prompt import PromptTemplate
from src.cxsim.econ.curves import Demand, Supply, SupplyDemand
from src.cxsim.gui.visualizer import GUI

import os
import openai


def main():
    openai.api_key = os.environ["openai_api_key"]

    env = Environment(
        max_steps=10,
        max_episodes=1,
        step_delay=1,
        gui=GUI()
    )

    total_agents = 15

    supply = Supply(total_agents)
    demand = Demand(total_agents)

    # Define Supply and Demand Functions
    demand.set_function(lambda x: (1 * x) + 140)
    supply.set_function(lambda x: 155 - (1 * x))

    sd = SupplyDemand(
        supply=supply,
        demand=demand
    )

    sd.plot()

    print(sd.find_equilibrium())

    buyer_pop = Population(
        agent=OpenAIAgent,
        number_of_agents=total_agents,
        system_prompt=PromptTemplate("src/cxsim/prompts/system_prompt.txt"),
        cognitive_prompt=PromptTemplate("src/cxsim/prompts/cognitive_prompt.txt"),
        decision_prompt=PromptTemplate("src/cxsim/prompts/decision_prompt.txt"),
        prompt_arguments={"role": "buyer"},
        agent_params={"goal": "buy shirts in the marketplace for a price lower than the expected value, you profit the difference. ", "shirts Expected Value": demand.values},
        agent_inventory={"capital": 1000, "shirts": 0}
    )

    seller_pop = Population(
        agent=OpenAIAgent,
        number_of_agents=total_agents,
        system_prompt=PromptTemplate("src/cxsim/prompts/system_prompt.txt"),
        cognitive_prompt=PromptTemplate("src/cxsim/prompts/cognitive_prompt.txt"),
        decision_prompt=PromptTemplate("src/cxsim/prompts/decision_prompt.txt"),
        prompt_arguments={"role": "seller"},
        agent_params={"goal": "sell shirts in the marketplace for a price higher than the expected value, you profit the difference", "shirts Expected Value": supply.values},
        agent_inventory={"capital": 1000, "shirts":  [2] * total_agents}
    )

    buyer_pop.shuffle()
    seller_pop.shuffle()

    for buyer, seller in zip(buyer_pop, seller_pop):
        env.add(buyer)
        env.add(seller)

    env.add(Marketplace())

    # prepare the environment to be run
    env.prepare()

    for episode in env.iter_episodes():
        for step in env.iter_steps():
            print(step)
            env.step()


if __name__ == '__main__':
    main()
