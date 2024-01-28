import time

import numpy as np
from cxsim import Environment, Population, Agent

from cxsim.artifacts.standard import Marketplace

from cxsim.agents.actions import ActionRestriction
from cxsim.artifacts.standard.marketplace import BuyOrder, SellOrder, MarketPlaceQuery
from cxsim.io.text.prompts.default_prompts import DEFAULT_DECISION_PROMPT, DEFAULT_SYSTEM_PROMPT
from cxsim.utilities.econ import Demand, Supply, SupplyDemand
from cxsim.agents.agent import after_turn


class MyAgent(Agent):
    def __init__(self):
        super().__init__()

    def compile(self):
        DEFAULT_SYSTEM_PROMPT.remove_section("Action Space")
        self.io.text.add_prompt(name="system", prompt=DEFAULT_SYSTEM_PROMPT)
        self.io.text.add_prompt("decision", DEFAULT_DECISION_PROMPT)

        artifact_descriptions = self.environment.utils.format.artifact_descriptions()
        action_restrictions = self.environment.utils.format_action_restrictions(self.action_restrictions)

        self.update_variables(
            {
                "name": self.name,
                "inventory": str(self.inventory.starting_inventory),
                "goal": str(self.params["goal"]),
                "action_restrictions": action_restrictions,
                "current_step": lambda: self.environment.current_step,
                "n_agents": str(len(self.environment.agents)),
                "max_steps": lambda: self.environment.max_steps,
                "agent_names": str(self.environment.agent_names),
                "num_artifacts": str(len(self.environment.artifacts)),
                "descriptions": artifact_descriptions,
                "observation": self.get_latest_observations,
                "history": self.get_latest_actions,
                "marketplace": self.environment["Marketplace"]["shirts"],
                "parameters": self.params,
                "price": self.params["shirts expected value"],
            }
        )

    def determine_action(self):
        if self.params["role"] == "buyer":
            action = BuyOrder("shirts", 10, 1)
        else:
            action = SellOrder("shirts", 1, 1)
        return action

    def reset(self):
        self.io.text.add_message("system", self.io.text.get_updated_prompt("system"))

    @after_turn
    def cleanup(self):
        self.io.text.format.compress_messages(n_steps_back=2)

    def step(self):
        print("agent step")
        self.io.text.add_message("user", self.io.text.get_updated_prompt("decision"))
        action = self.determine_action()
        time.sleep(1)
        _action = "SellOrder('shirts', 1, 1)"
        _actiontwo = "BuyOrder(good='shirts', quantity = 1, price = 1)"

        observation = self.environment.execute(self, action)

        self.io.text.add_message(role="assistant", content=str(action))

        return None


def calculate_alpha(equilibrium, price_history):
    std_around_eq = abs(price_history - equilibrium) ** 2
    std_around_eq = np.sqrt(np.mean(std_around_eq))
    return 100 * (std_around_eq / equilibrium)


class Smith1962Environment:
    def __init__(self, n_agents: int, model_id: str = "gpt-3.5-turbo", equilibrium_price: int = 50):
        self.model_id = model_id
        self._n_agents = int(n_agents // 2)
        self.equilibrium_price = equilibrium_price

        self._b = 1  # Slope for supply curve
        self._d = 1  # Slope for demand curve

        self.shift_value = self._n_agents / 2

        # Calculate a and c based on the number of agents
        self._a = (self._n_agents / 2) + (self.equilibrium_price - self.shift_value)
        self._c = (self._n_agents / 2) + (self.equilibrium_price + self.shift_value)

    def _supply_function(self, x: float) -> float:
        """Supply function S(x) = a + bx"""
        return self._a + self._b * x

    def _demand_function(self, x: float) -> float:
        """Demand function D(x) = c - dx"""
        return self._c - self._d * x

    def test_shift(
            self,
            plot_supply_demand: bool = False,
            market_depth: int = 5,
    ):
        pass

    def test_one(self, plot_supply_demand: bool = False, market_depth: int = 5):
        supply = Supply(
            prices=self._supply_function,
            quantities=lambda x: x,
            max_quantity=self._n_agents + 1
        )

        demand = Demand(
            prices=self._demand_function,
            quantities=lambda x: x,
            max_quantity=self._n_agents + 1
        )

        env = Environment(
            name="Smith 1962",
            max_steps=30,
            max_episodes=1,
            step_delay=1
        )

        sd = SupplyDemand(supply=supply, demand=demand)

        if plot_supply_demand:
            sd.plot()

        equilibrium_quantity, equilibrium_price = sd.find_equilibrium()

        market = Marketplace(market_depth=market_depth)

        market.action_space.remove(MarketPlaceQuery)

        env.add(market)

        print(market.action_space)

        def buy_limit(agent, action):
            assert agent.params["shirts expected value"] > action.price, "You placed a buy order with a price higher than your expected value"

        def sell_limit(agent, action):
            assert agent.params["shirts expected value"] < action.price, "You placed a sell order with a price lower than your expected value"

        buyer_pop = Population(
            agent=MyAgent,
            number_of_agents=self._n_agents,
            action_restrictions=[ActionRestriction(action=BuyOrder, func=buy_limit)],
            agent_params={
                "role": "buyer",
                "goal": "buy shirts in the marketplace for a price lower than your expected value, you profit the difference. Only buy one shirt at a time",
                "shirts expected value": demand.prices
            },
            agent_inventory={"capital": 1255, "shirts": 0}
        )

        seller_pop = Population(
            agent=MyAgent,
            number_of_agents=self._n_agents,
            action_restrictions=[ActionRestriction(action=SellOrder, func=sell_limit)],
            agent_params={
                "role": "seller",
                "goal": "maximize your capital by selling shirts in the marketplace for a price higher than the expected value. You profit the difference. Only sell one shirt at a time ",
                "shirts expected value": supply.prices
            },
            agent_inventory={"capital": 1255, "shirts": supply.quantities}
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

#                price_history = market["shirts"].history["price"]

        #        if len(price_history) != 0:
          #          alpha = calculate_alpha(equilibrium_price, price_history)
           #         alpha_history.append(alpha)

               # print(f"""STEP {env.current_step}\nEquilibrium Price: {equilibrium_price}\nprevious transactions: {price_history}\nalpha values: {alpha_history}""")

                env.step()


if __name__ == '__main__':
    env = Smith1962Environment(
        n_agents=10
    )

    env.test_one()

