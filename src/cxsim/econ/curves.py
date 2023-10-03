import numpy as np
import plotly.graph_objs as go
from scipy.optimize import fsolve


class EconomicCurve:
    """Base class for economic curves like Supply and Demand."""

    def __init__(self, total_agents: int):
        self.total_agents = total_agents
        self.values = None
        self.func = None  # Store the function itself

    def set_function(self, func):
        self.func = func  # Store the function
        self.values = [func(x) for x in range(self.total_agents)]

    def shift_curve(self, shift_value: int):
        """Shift the curve up or down by the given value."""
        self.values = [x + shift_value for x in self.values]

    def plot(self):
        return go.Figure(
            go.Scatter(
                x=[_ for _ in range(self.total_agents)],
                y=self.values
            )
        )


class Supply(EconomicCurve):
    """Class to manage supply curve and related metrics."""

    def calculate_producer_surplus(self, equilibrium_price: int) -> float:
        """Calculate the producer surplus given an equilibrium price."""
        return 0.5 * (equilibrium_price - self.values[-1]) * self.total_agents


class Demand(EconomicCurve):
    """Class to manage demand curve and related metrics."""

    def calculate_consumer_surplus(self, equilibrium_price: int) -> float:
        """Calculate the consumer surplus given an equilibrium price."""
        return 0.5 * (self.values[0] - equilibrium_price) * self.total_agents


class SupplyDemand:
    def __init__(self, supply: Supply, demand: Demand):
        self.supply = supply
        self.demand = demand

    def find_equilibrium(self):
        def equation(q):
            return self.supply.func(q) - self.demand.func(q)

        equilibrium_quantity = fsolve(equation, 0)[0]
        equilibrium_price = self.supply.func(equilibrium_quantity)

        return equilibrium_price, equilibrium_quantity

    def plot(self):
        fig = go.Figure()

        # Plot supply curve
        fig.add_trace(
            go.Scatter(
                x=[_ for _ in range(self.supply.total_agents)],
                y=self.supply.values,
                mode='lines',
                name='Supply'
            )
        )

        # Plot demand curve
        fig.add_trace(
            go.Scatter(
                x=[_ for _ in range(self.demand.total_agents)],
                y=self.demand.values,
                mode='lines',
                name='Demand'
            )
        )

        # Find and plot equilibrium point if it exists
        equilibrium_price, equilibrium_quantity = self.find_equilibrium()
        if equilibrium_price is not None:
            fig.add_trace(
                go.Scatter(
                    x=[equilibrium_quantity],
                    y=[equilibrium_price],
                    mode='markers',
                    name='Equilibrium',
                    marker=dict(size=10, color='red')
                )
            )

        fig.show()

