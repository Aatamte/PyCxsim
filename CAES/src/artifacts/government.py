from CAES.src.core import Agent
from CAES.src.artifacts.artifact import Artifact


class Government(Artifact):
    def __init__(self, tax_rate, public_good_value):
        super().__init__("Government")
        self.tax_rate = tax_rate
        self.public_good_value = public_good_value

    def execute(self, agent, action_details):
        action = action_details
        if action == "pay_tax":
            self.collect_tax(agent)

    def collect_tax(self, agent):
        tax = self.tax_rate * agent.inventory.get_quantity('money')
        if tax > 0:
            agent.inventory.remove_item('money', tax)

    def provide_public_good(self):
        # Here we just return the value of the public good.
        # In a more detailed simulation, you might distribute this value among the agents,
        # or use it to affect the state of the environment or the agents.
        return self.public_good_value

    def generate_observations(self, agents):
        return {
            'tax_rate': self.tax_rate,
            'public_good_value': self.public_good_value,
        }

    def should_continue(self):
        # A government might stop the simulation if it runs out of money or if the public good value is too low.
        # Here, we just return True so the simulation always continues.
        return True
