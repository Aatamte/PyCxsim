from src.CAES import Artifact


class CentralBank(Artifact):
    def __init__(self):
        super().__init__("CentralBank")
        self.interest_rate = 0.01  # The initial interest rate
        self.money_supply = 10000  # The initial money supply

    def execute(self, agent, action_details):
        # We might imagine that the central bank's actions are not directly controlled by agents,
        # but are determined by the state of the economy.
        # So in this case, we don't need to implement the execute method.
        pass

    def set_interest_rate(self, rate):
        self.interest_rate = rate
        # We could imagine that changing the interest rate has some effect on the economy,
        # but for simplicity, we won't model that effect here.

    def quantitative_easing(self, amount):
        self.money_supply += amount
        # Here, we could add some logic to distribute the new money among the agents in the simulation.
        # For example, we could increase each agent's bank account balance proportionally to its current balance.
        # We could also change the interest rate in response to the increased money supply.

    def generate_observations(self, agents):
        return {
            'interest_rate': self.interest_rate,
            'money_supply': self.money_supply,
        }

    def should_continue(self):
        # A central bank might stop the simulation if the economy is in a bad state,
        # such as if the money supply is too high or too low.
        # Here, we just return True so the simulation always continues.
        return True
