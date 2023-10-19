from cxsim import Environment, Population, PromptTemplate
from cxsim.artifacts import Marketplace
from cxsim.agents import OpenAIAgent
from cxsim.actions.action_restrictions import ActionRestriction
from cxsim.artifacts.marketplace import BuyOrder, SellOrder, MarketPlaceQuery
from cxsim.prompts.default_prompts import DEFAULT_DECISION_PROMPT, DEFAULT_SYSTEM_PROMPT
from cxsim.econ import Demand, Supply, SupplyDemand

import os
import openai
import numpy as np
from typing import Union, List

class SmithAgent(OpenAIAgent):
    def __init__(self):
        super().__init__()
        self.connection.system_prompt = DEFAULT_SYSTEM_PROMPT
        self.decision_prompt = DEFAULT_DECISION_PROMPT

    def reset(self):
        self.connection.system_prompt.set_variables(
            {
                "name": self.name,
                "inventory": str(self.inventory.starting_inventory),
                "goal": str(self.params["goal"]),
                "action_restrictions": self.connection.system_prompt.sections["Action Restrictions"].format_list(
                    self.action_restrictions),
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
                "parameters": str(self.params)
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


class Smith1962Environment:
    def __init__(self, n_agents: int, model: str = "gpt-3.5-turbo", equilibrium_price: int = 50):
        self.model = model
        self.n_agents = n_agents
        self.equilibrium_price = equilibrium_price

        self.b = 1  # Slope for supply curve
        self.d = 1  # Slope for demand curve

        self.shift_value = self.n_agents / 2

        # Calculate a and c based on the number of agents
        self.a = (self.n_agents / 2) + (self.equilibrium_price - self.shift_value)
        self.c = (self.n_agents / 2) + (self.equilibrium_price + self.shift_value)

    def supply_function(self, x: float) -> float:
        """Supply function S(x) = a + bx"""
        return self.a + self.b * x

    def demand_function(self, x: float) -> float:
        """Demand function D(x) = c - dx"""
        return self.c - self.d * x

    def test(self, n: int):
        pass

    def test_one(self):
        supply = Supply(
            prices=self.supply_function,
            quantities=lambda x: x,
            max_quantity=self.n_agents + 1
        )

        demand = Demand(
            prices=self.demand_function,
            quantities=lambda x: x,
            max_quantity=self.n_agents + 1
        )

        env = Environment(
            max_steps=30,
            max_episodes=1,
            step_delay=1
        )

        sd = SupplyDemand(supply=supply, demand=demand)

        equilibrium_quantity, equilibrium_price = sd.find_equilibrium()

        sd.plot()

        market = Marketplace()

        market.action_space.remove(MarketPlaceQuery)

        env.add(market)

        def buy_limit(agent, action):
            assert agent.params[
                       "shirts expected value"] > action.price, f"You placed a buy order with a price higher than your expected value, {agent.name} | {agent.params['shirts expected value']} | {action.price}"

        def sell_limit(agent, action):
            assert agent.params[
                       "shirts expected value"] < action.price, f"You placed a sell order with a price lower than your expected value"
        SmithAgent.model_id = self.model
        buyer_pop = Population(
            agent=SmithAgent,
            number_of_agents=self.n_agents,
            action_restrictions=[ActionRestriction(action=BuyOrder, func=buy_limit)],
            prompt_arguments={"role": "buyer"},
            agent_params={
                "goal": "buy shirts in the marketplace for a price lower than your expected value, you profit the difference. Only buy one shirt at a time",
                "shirts expected value": demand.prices
            },
            agent_inventory={"capital": 1255, "shirts": 0}
        )

        seller_pop = Population(
            agent=SmithAgent,
            number_of_agents=self.n_agents,
            action_restrictions=[ActionRestriction(action=SellOrder, func=sell_limit)],
            prompt_arguments={"role": "seller"},
            agent_params={
                "goal": "maximize your capital by selling shirts in the marketplace for a price higher than the expected value. You profit the difference. Only sell one shirt at a time ",
                "shirts expected value": supply.prices
            },
            agent_inventory={"capital": 1255, "shirts": [25] * self.n_agents}
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

                if len(price_history) != 0:
                    alpha = calculate_alpha(equilibrium_price, price_history)
                    alpha_history.append(alpha)

                print(f"""STEP {env.current_step}\nprevious transactions: {price_history}\nalpha values: {alpha_history}""")

                env.step()
