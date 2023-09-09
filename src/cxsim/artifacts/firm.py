from src.cxsim import Artifact


class Firm(Artifact):
    def __init__(self, wage_rate, production_function, goods_price):
        super().__init__("Firm")
        self.wage_rate = wage_rate
        self.production_function = production_function
        self.goods_price = goods_price
        self.workers = []  # List of Agent ids

    def execute(self, agent, action_details):
        action = action_details
        if action == "apply":
            self.hire(agent)

    def hire(self, agent):
        # Hire a worker
        self.workers.append(agent.id)
        agent.inventory.add_item('money', self.wage_rate)  # Pay the worker

    def produce_goods(self):
        # Apply the production function to the amount of labor
        labor = len(self.workers)
        goods = self.production_function(labor)
        return goods

    def sell_goods(self, goods):
        # Sell the goods and earn money
        earnings = goods * self.goods_price
        return earnings

    def generate_observations(self):
        return {
            'wage_rate': self.wage_rate,
            'goods_price': self.goods_price,
            'number_of_workers': len(self.workers),
        }

    def should_continue(self):
        # A firm might stop the simulation if it runs out of money or if it has too few workers.
        # Here, we just return True so the simulation always continues.
        return True
