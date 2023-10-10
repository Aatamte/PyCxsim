from src.cxsim import Environment, Population, GUI, PromptTemplate
from src.cxsim.artifacts import Marketplace, Dialogue, Gridworld, Artifact
from src.cxsim.agents import OpenAIAgent
from src.cxsim.actions.action_restrictions import ActionRestriction
from src.cxsim.artifacts.marketplace import BuyOrder, SellOrder, MarketPlaceQuery

from src.cxsim.econ import Demand, Supply, SupplyDemand

import os
import openai
import numpy as np


def calculate_alpha(equilibrium, price_history):
    std_around_eq = abs(price_history - equilibrium) ** 2
    std_around_eq = np.sqrt(np.mean(std_around_eq))
    return 100 * (std_around_eq / equilibrium)


def test(total_agents, supply: Supply, demand: Demand):
    openai.api_key = os.environ["openai_api_key"]
    GOOD = "shirts"

    env = Environment(
        max_steps=30,
        max_episodes=1,
        step_delay=1,
        gui=GUI()
    )

    sd = SupplyDemand(supply=supply, demand=demand)

    equilibrium_quantity, equilibrium_price = sd.find_equilibrium()

    print(equilibrium_price)

    def buy_limit(agent, action):
        assert agent.params["shirts expected value"] > action.price, f"You placed a buy order with a price higher than your expected value, {agent.name} | {agent.params['shirts expected value']} | {action.price}"

    def sell_limit(agent, action):
        assert agent.params["shirts expected value"] < action.price, f"You placed a sell order with a price lower than your expected value"

    buyer_pop = Population(
        agent=OpenAIAgent,
        number_of_agents=total_agents,
        system_prompt=PromptTemplate("src/cxsim/prompts/system_prompt.txt"),
        decision_prompt=PromptTemplate("src/cxsim/prompts/decision_prompt.txt"),
        action_restrictions=[
            ActionRestriction(action=BuyOrder, func=buy_limit)
        ],
        prompt_arguments={"role": "buyer"},
        agent_params={
            "goal": "buy shirts in the marketplace for a price lower than your expected value, you profit the difference. Only buy one shirt at a time",
            "shirts expected value": demand.prices
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
        decision_prompt=PromptTemplate("src/cxsim/prompts/decision_prompt.txt"),
        action_restrictions=[
            ActionRestriction(action=SellOrder, func=sell_limit)
        ],
        prompt_arguments={"role": "seller"},
        agent_params={
            "goal": "maximize your capital by selling shirts in the marketplace for a price higher than the expected value. You profit the difference. Only sell one shirt at a time ",
            "shirts expected value": supply.prices
        },
        agent_inventory={
            "capital": 1255,
            "shirts": [25] * total_agents
        }
    )

    buyer_pop.shuffle()
    seller_pop.shuffle()

    for buyer, seller in zip(buyer_pop, seller_pop):
        env.add(buyer)
        env.add(seller)

    market = Marketplace()

    market.action_space.remove(MarketPlaceQuery)
    print(market.action_space)

    env.add(market)

    alpha_history = []

    for episode in env.iter_episodes():
        env.reset()

        for step in env.iter_steps():
            for agent in env.iter_agent_turns():
                agent.decision_prompt.set_variable("marketplace", str(market["shirts"]), "decision prompt")
                env.process_turn(agent)

                price_history = market["shirts"].history["price"].values
                print(price_history)
                if len(price_history) != 0:
                    alpha = calculate_alpha(equilibrium_price, price_history)
                    print(alpha)
                    alpha_history.append(alpha)

            env.step()


if __name__ == '__main__':

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

    test(
        total_agents,
        supply,
        demand
    )

