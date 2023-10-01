import numpy as np


class EconomicCurve:
    """Base class for economic curves like Supply and Demand."""

    def __init__(self, total_agents: int):
        self.total_agents = total_agents
        self.function = None

    def set_function(self, func):
        """Set the function and populate it for the given range of agents."""
        self.function = np.array([func(x) for x in range(self.total_agents)], dtype=int).tolist()

    def shift_curve(self, shift_value: int):
        """Shift the curve up or down by the given value."""
        self.function = [x + shift_value for x in self.function]


class Supply(EconomicCurve):
    """Class to manage supply curve and related metrics."""

    def calculate_producer_surplus(self, equilibrium_price: int) -> float:
        """Calculate the producer surplus given an equilibrium price."""
        return 0.5 * (equilibrium_price - self.function[-1]) * self.total_agents


class Demand(EconomicCurve):
    """Class to manage demand curve and related metrics."""

    def calculate_consumer_surplus(self, equilibrium_price: int) -> float:
        """Calculate the consumer surplus given an equilibrium price."""
        return 0.5 * (self.function[0] - equilibrium_price) * self.total_agents