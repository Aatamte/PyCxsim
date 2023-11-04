from cxsim import Environment, Population, PromptTemplate
from cxsim.artifacts import Marketplace
from cxsim.agents import Agent
from cxsim.actions.action_restrictions import ActionRestriction
from cxsim.artifacts.marketplace import BuyOrder, SellOrder, MarketPlaceQuery
from cxsim.prompts.default_prompts import DEFAULT_DECISION_PROMPT, DEFAULT_SYSTEM_PROMPT
from cxsim.econ import Demand, Supply, SupplyDemand
from cxsim.agents.backends.language_backend import LanguageBackend

import numpy as np

MODEL_ID = ""


class SmithAgent(Agent):
    def __init__(self, model_id):
        super().__init__()
        self.backend = LanguageBackend(model_id=model_id)
        self.system_prompt = DEFAULT_SYSTEM_PROMPT
        self.decision_prompt = DEFAULT_DECISION_PROMPT
        self.functions = None

    def reset(self):
        artifact_descriptions = self.environment.utils.format_artifact_descriptions(self.environment.artifacts)
        action_restrictions = self.environment.utils.format_action_restrictions(self.action_restrictions)

        self.system_prompt.set_variables(
            {
                "name": self.name,
                "inventory": str(self.inventory.starting_inventory),
                "goal": str(self.params["goal"]),
                "action_restrictions": action_restrictions,
                "n_agents": str(len(self.environment.agents)),
                "max_steps": str(self.environment.max_steps),
                "agent_names": str(self.environment.agent_names),
                "num_artifacts": str(len(self.environment.action_handler.artifacts)),
                "descriptions": artifact_descriptions
            }
        )

        self.system_prompt.remove_section("Action Space")
        self.backend.add_message("system", self.system_prompt)

        self.functions = self.environment.utils.format_openai_function_calls(self.action_space_list)

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
                "current_step": self.environment.current_step,
                "goal": self.params["goal"],
                "max_steps": self.environment.max_steps,
                "observation": observation,
                "history": str(action_history),
                "marketplace": shirts_orderbook,
                "price": self.params["shirts expected value"],
                "parameters": str(self.params)
            }
        )

        self.backend.add_message("user", self.decision_prompt)
        func_name = "buyorder" if self.params["role"] == "buyer" else "sellorder"

        response = self.backend.complete(
            functions=self.functions,
            function_call={"name": func_name}
        )

        content, func_call = self.backend.openai.parse_function_call(response)

        pretty_func_call = self.backend.openai.format_function_call(func_call)

        self.backend.add_message("assistant", pretty_func_call)

        observation = self.environment.process_action(self, func_call)

        self.observations.append(observation)

        self.backend.compress_messages(n_steps_back=2)

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

        def buy_limit(agent, action):
            assert agent.params["shirts expected value"] > action.price, "You placed a buy order with a price higher than your expected value"

        def sell_limit(agent, action):
            assert agent.params["shirts expected value"] < action.price, "You placed a sell order with a price lower than your expected value"

        buyer_pop = Population(
            agent=SmithAgent,
            agent_kargs={"model_id": self.model_id},
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
            agent=SmithAgent,
            agent_kargs={"model_id": self.model_id},
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

                price_history = market["shirts"].history["price"].values

                if len(price_history) != 0:
                    alpha = calculate_alpha(equilibrium_price, price_history)
                    alpha_history.append(alpha)

                print(f"""STEP {env.current_step}\nEquilibrium Price: {equilibrium_price}\nprevious transactions: {price_history}\nalpha values: {alpha_history}""")

                env.step()
