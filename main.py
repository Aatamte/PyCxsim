from cxsim import Environment, Population, PromptTemplate
from cxsim.artifacts import Marketplace
from cxsim.agents import OpenAIAgent
from cxsim.actions.action_restrictions import ActionRestriction
from cxsim.artifacts.marketplace import BuyOrder, SellOrder, MarketPlaceQuery

from cxsim.econ import Demand, Supply, SupplyDemand

import os
import openai
import numpy as np


class MyAgent(OpenAIAgent):
    def __init__(self):
        super().__init__()
        self.connection.system_prompt = PromptTemplate("src/cxsim/prompts/system_prompt.txt")
        self.decision_prompt = PromptTemplate("src/cxsim/prompts/decision_prompt.txt")

    def reset(self):
        self.connection.system_prompt.set_variables(
            {
                "name": self.name,
                "inventory": str(self.inventory.starting_inventory),
                "goal": str(self.params["goal"]),
                "action_restrictions": self.connection.system_prompt.sections["Action Restrictions"].format_list(self.action_restrictions),
                "n_agents": str(len(self.environment.agents)),
                "max_steps": str(self.environment.max_steps),
                "agent_names": str(self.environment.agent_names),
                "num_artifacts": str(len(self.environment.action_handler.artifacts))
            }
        )
        self.connection.system_prompt.set_artifact_descriptions(self.environment.artifacts)

        self.connection.system_prompt.remove_section("Action Restrictions")
        self.add_message("system", self.connection.system_prompt.get_prompt())

        for artifact, action_list in self.action_space.items():
            for action in action_list:
                self.connection.function_definitions.append(
                    self.environment.utils.format_openai_function_call(action)
                )

    def step(self):
        if len(self.observations) != 0:
            observation = self.observations.pop(0)
        else:
            observation = "N/A"

        if len(self.action_history) >= 1:
            action_history = self.action_history[-1]
        elif len(self.action_history) == 0:
            action_history = "N/A"
        else:
            action_history = self.action_history

        marketplace = self.environment["Marketplace"]
        shirts_orderbook = marketplace["shirts"]

        self.decision_prompt.set_variables(
            {
                "inventory": str(self.display_inventory()),
                "inbox": str(self.inbox),
                "current_step": self.environment.current_step,
                "goal": self.params["goal"],
                "max_steps": self.environment.max_steps,
                "observation": observation,
                "history": str(action_history),
                "marketplace": shirts_orderbook,
                "parameters": self.params
            }
        )
        self.add_message("user", self.decision_prompt.get_prompt())

        response = self.connection.complete(action_needed=True)

        action = self.connection.function_calls.pop(0)

        observation = self.environment.process_action(self, action)

        return None


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
        step_delay=1
    )

    sd = SupplyDemand(supply=supply, demand=demand)

    equilibrium_quantity, equilibrium_price = sd.find_equilibrium()

    market = Marketplace()

    market.action_space.remove(MarketPlaceQuery)

    env.add(market)

    def buy_limit(agent, action):
        assert agent.params["shirts expected value"] > action.price, f"You placed a buy order with a price higher than your expected value, {agent.name} | {agent.params['shirts expected value']} | {action.price}"

    def sell_limit(agent, action):
        assert agent.params["shirts expected value"] < action.price, f"You placed a sell order with a price lower than your expected value"

    buyer_pop = Population(
        agent=MyAgent,
        number_of_agents=total_agents,
        action_restrictions=[ActionRestriction(action=BuyOrder, func=buy_limit)],
        prompt_arguments={"role": "buyer"},
        agent_params={
            "goal": "buy shirts in the marketplace for a price lower than your expected value, you profit the difference. Only buy one shirt at a time",
            "shirts expected value": demand.prices
        },
        agent_inventory={"capital": 1255, "shirts": 0}
    )

    seller_pop = Population(
        agent=MyAgent,
        number_of_agents=total_agents,
        action_restrictions=[ActionRestriction(action=SellOrder, func=sell_limit)],
        prompt_arguments={"role": "seller"},
        agent_params={
            "goal": "maximize your capital by selling shirts in the marketplace for a price higher than the expected value. You profit the difference. Only sell one shirt at a time ",
            "shirts expected value": supply.prices
        },
        agent_inventory={"capital": 1255, "shirts": [25] * total_agents}
    )

    buyer_pop.shuffle()
    seller_pop.shuffle()

    for buyer, seller in zip(buyer_pop, seller_pop):
        env.add(buyer)
        env.add(seller)

    alpha_history = []

    for episode in env.iter_episodes():
        env.reset()

        for step in env.iter_steps():
            for agent in env.iter_agent_turns():
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

