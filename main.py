from src.cxsim import Environment, Population, GUI, PromptTemplate
from src.cxsim.artifacts import Marketplace, Dialogue, Gridworld, Artifact
from src.cxsim.agents import OpenAIAgent

from src.cxsim.econ import Demand, Supply, SupplyDemand

import os
import openai


def main():
    openai.api_key = os.environ["openai_api_key"]

    env = Environment(
        max_steps=30,
        max_episodes=1,
        step_delay=1,
        gui=GUI()
    )

    total_agents = 15

    # Create Supply and Demand instances with explicit prices and quantities
    supply = Supply(
        prices=lambda x: 50 + x,
        quantities=lambda x: x,
        max_quantity=total_agents + 1
    )

    demand = Demand(
        prices=lambda x: 65 - x,
        quantities=lambda x: x,
        max_quantity=total_agents + 1
    )

    sd = SupplyDemand(supply=supply, demand=demand)

    print(sd.find_equilibrium())

    sd.plot()

    buyer_pop = Population(
        agent=OpenAIAgent,
        number_of_agents=total_agents,
        system_prompt=PromptTemplate("src/cxsim/prompts/system_prompt.txt"),
        cognitive_prompt=PromptTemplate("src/cxsim/prompts/cognitive_prompt.txt"),
        decision_prompt=PromptTemplate("src/cxsim/prompts/decision_prompt.txt"),
        prompt_arguments={"role": "buyer"},
        agent_params={
            "goal": "buy shirts in the marketplace for a price lower than the expected value, you profit the difference.",
            "shirts Expected Value": demand.prices
        },
        agent_inventory={
            "capital": 1255,
            "shirts": 0
        }
    )

    seller_pop = Population(
        agent=OpenAIAgent,
        number_of_agents=total_agents,
        system_prompt=PromptTemplate("src/cxsim/prompts/system_prompt.txt"),
        cognitive_prompt=PromptTemplate("src/cxsim/prompts/cognitive_prompt.txt"),
        decision_prompt=PromptTemplate("src/cxsim/prompts/decision_prompt.txt"),
        prompt_arguments={"role": "seller"},
        agent_params={
            "goal": "sell shirts in the marketplace for a price higher than the expected value, you profit the difference. You may only sell one at a time",
            "shirts Expected Value": supply.prices
        },
        agent_inventory={
            "capital": 1255,
            "shirts":  [10] * total_agents
        }
    )

    buyer_pop.shuffle()
    seller_pop.shuffle()

    for buyer, seller in zip(buyer_pop, seller_pop):
        env.add(buyer)
        env.add(seller)

    market = Marketplace(

    )
    env.add(market)

    for episode in env.iter_episodes():
        env.reset()

        for step in env.iter_steps():

            for agent in env.iter_agent_turns():
                env.process_turn(agent)

            env.step()


if __name__ == '__main__':
    main()
