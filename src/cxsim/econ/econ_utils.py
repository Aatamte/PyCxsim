from scipy.optimize import minimize, root, fsolve, least_squares, differential_evolution, basinhopping
import numpy as np


class EquilibriumFinder:
    def __init__(self, supply, demand, decimals: int = 2):
        self.supply = supply
        self.demand = demand
        self.decimals = decimals

    def equation(self, q):
        supply_price = np.interp(q, self.supply.quantities, self.supply.prices)
        demand_price = np.interp(q, self.demand.quantities, self.demand.prices)
        return supply_price - demand_price

    def find_with_minimize(self):
        result = minimize(lambda x: abs(self.equation(x)), 0, method='BFGS')
        equilibrium_quantity = round(result.x[0], self.decimals)
        equilibrium_price = round(np.interp(equilibrium_quantity, self.supply.quantities, self.supply.prices), self.decimals)
        return equilibrium_quantity, equilibrium_price

    def find_with_root(self):
        result = root(self.equation, 0)
        equilibrium_quantity = round(result.x[0], self.decimals)
        equilibrium_price = round(np.interp(equilibrium_quantity, self.supply.quantities, self.supply.prices),
                                  self.decimals)
        return equilibrium_quantity, equilibrium_price

    def find_with_fsolve(self):
        q_value = fsolve(self.equation, 0)[0]
        equilibrium_price = np.interp(q_value, self.supply.quantities, self.supply.prices)
        return round(q_value, self.decimals), round(equilibrium_price, self.decimals)

    def find_with_least_squares(self):
        result = least_squares(self.equation, 0)
        equilibrium_quantity = round(result.x[0], self.decimals)
        equilibrium_price = round(np.interp(equilibrium_quantity, self.supply.quantities, self.supply.prices),
                                  self.decimals)
        return equilibrium_quantity, equilibrium_price

    def find_with_differential_evolution(self):
        result = differential_evolution(lambda x: abs(self.equation(x)), [(0, 100)])
        equilibrium_quantity = round(result.x[0], self.decimals)
        equilibrium_price = round(np.interp(equilibrium_quantity, self.supply.quantities, self.supply.prices),
                                  self.decimals)
        return equilibrium_quantity, equilibrium_price

    def find_with_basinhopping(self):
        result = basinhopping(lambda x: abs(self.equation(x)), 0)
        equilibrium_quantity = round(result.x[0], self.decimals)
        equilibrium_price = round(np.interp(equilibrium_quantity, self.supply.quantities, self.supply.prices),
                                  self.decimals)
        return equilibrium_quantity, equilibrium_price

    def find(self, method):
        if method == 'minimize':
            return self.find_with_minimize()
        elif method == 'root':
            return self.find_with_root()
        elif method == 'fsolve':
            return self.find_with_fsolve()
        elif method == 'least_squares':
            return self.find_with_least_squares()
        elif method == 'differential_evolution':
            return self.find_with_differential_evolution()
        elif method == 'basinhopping':
            return self.find_with_basinhopping()
        else:
            return "Invalid method"


if __name__ == '__main__':
    # Example usage
    supply_func = lambda x: 50 + 2 * x + 0.1 * x ** 2
    demand_func = lambda x: 200 - 2 * x - 0.2 * x ** 2

    finder = EquilibriumFinder(supply_func, demand_func)

    print("Using minimize:", finder.find('minimize'))
    print("Using root:", finder.find('root'))
    print("Using fsolve:", finder.find('fsolve'))
    print("Using least_squares:", finder.find('least_squares'))
    print("Using differential_evolution:", finder.find('differential_evolution'))
    print("Using basinhopping:", finder.find('basinhopping'))