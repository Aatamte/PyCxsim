import numpy as np
import plotly.graph_objs as go
from scipy.optimize import fsolve
from collections.abc import Callable

from cxsim.econ.econ_utils import EquilibriumFinder


class EconomicCurve:
    """Base class for economic curves like Supply and Demand."""

    def __init__(self, prices, quantities, max_price=1000, max_quantity=1000):
        self.max_price = max_price
        self.max_quantity = max_quantity
        self.prices_func = None
        self.quantity_func = None

        # Check the type of prices and quantities and set them accordingly
        if isinstance(prices, list) and isinstance(quantities, Callable):
            self.quantity_func = quantities
            self.prices = prices
            self.quantities = [quantities(i) for i in range(self.max_quantity)]
        elif isinstance(quantities, list) and isinstance(prices, Callable):
            self.prices_func = prices
            self.quantities = quantities
            self.prices = [prices(i) for i in range(len(quantities))]
        elif isinstance(prices, list) and isinstance(quantities, list):
            min_length = min(len(prices), len(quantities))
            self.prices = prices[:min_length]
            self.quantities = quantities[:min_length]
        elif isinstance(prices, Callable) and isinstance(quantities, Callable):
            self.quantities = [quantities(i) for i in range(self.max_quantity)]
            self.prices = [prices(i) for i in self.quantities]
        else:
            raise ValueError("Invalid types for prices and quantities")

    def shift_prices_by_function(self, shift_func):
        """Shift prices based on a provided function."""
        self.prices = [shift_func(p) for p in self.prices]

    def shift_quantity_by_function(self, shift_func):
        """Shift quantity based on a provided function."""
        self.quantities = [shift_func(q) for q in self.quantities]

    def plot(self):
        return go.Figure(
            go.Scatter(
                x=self.quantities,
                y=self.prices
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
    def __init__(self, supply: EconomicCurve, demand: EconomicCurve, optimization_method: str = "minimize"):
        self.supply = supply
        self.demand = demand
        self.optimization_method = optimization_method

    def find_equilibrium(self):
        return EquilibriumFinder(
            demand=self.demand,
            supply=self.supply
        ).find(
            self.optimization_method
        )

    def plot(self):
        # Determine the common range of quantities based on the available data
        min_quantity = max(min(self.supply.quantities), min(self.demand.quantities))
        max_quantity = min(max(self.supply.quantities), max(self.demand.quantities))

        min_prices = max(min(self.supply.prices), min(self.demand.prices))
        max_prices = min(max(self.supply.prices), max(self.demand.prices))

        fig = go.Figure()

        # Plot supply curve within the determined range
        fig.add_trace(
            go.Scatter(
                x=self.supply.quantities,
                y=self.supply.prices,
                mode='lines',
                name='Supply'
            )
        )

        # Plot demand curve within the determined range
        fig.add_trace(
            go.Scatter(
                x=self.demand.quantities,
                y=self.demand.prices,
                mode='lines',
                name='Demand'
            )
        )

        # Find and plot equilibrium point if it exists
        equilibrium_quantity, equilibrium_price = self.find_equilibrium()
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
        print(min_quantity, max_quantity)

        # Automatically adjust the axis limits
        fig.update_xaxes(range=[min_quantity, max_quantity])
        fig.update_yaxes(range=[min_prices, max_prices])

        fig.show()

