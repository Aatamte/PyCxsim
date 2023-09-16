import unittest
from src.cxsim import Environment
from src.cxsim.agents import Agent
from src.cxsim.artifacts.marketplace import Marketplace, Order
import random


class DummyAgent(Agent):
    def __init__(self, name):
        super(DummyAgent, self).__init__(name)
        self.inventory.set_starting_inventory(
            {"capital": 1000, "socks": 100}
        )

    def execute_action(self):
        # Sample order for demonstration. Adjust parameters as needed.
        sample_order = Order(good="socks", price=10, quantity=5)
        self.action_queue.append(sample_order)

    def execute_query(self):
        return None

# Assuming basic stubs for Environment, Agent, and Order classes

# The actual integration test:


class TestOrderBookIntegration(unittest.TestCase):
    def setUp(self):
        # Setup the environment
        self.environment = Environment()

        # Create and add 10 DummyAgent instances to the environment
        self.agents = [DummyAgent(f"Agent_{i}") for i in range(10)]
        for agent in self.agents:
            self.environment.add(agent)

        # Add a Marketplace to the environment
        self.marketplace = Marketplace()
        self.marketplace.create_market("socks")
        self.environment.add(self.marketplace)

        self.environment.prepare()

    def test_buy_order_exceeds_capital(self):
        agent = self.agents[0]
        agent.execute_action()  # Agent creates a buy order for 10 socks at $5 each ($50 total)

        # Now, we manually create a buy order which would exceed the agent's capital when combined with the existing order
        expensive_order = Order(good="socks", price=1000, quantity=5)
        self.marketplace.process_action(agent, expensive_order)

        # Only the initial buy order should exist, the expensive order should be ignored
        self.assertEqual(len(self.marketplace["socks"].buy_orders), 1)

    def test_sell_order_exceeds_goods(self):
        agent = self.agents[0]
        # The agent will try to sell more socks than they have
        sell_order_1 = Order(good="socks", price=10, quantity=-110)
        sell_order_2 = Order(good="socks", price=10, quantity=-10)
        self.marketplace.process_action(agent, sell_order_1)
        self.marketplace.process_action(agent, sell_order_2)

        # No sell orders should exist, since the agent doesn't have enough socks
        self.assertEqual(len(self.marketplace["socks"].sell_orders), 1)

    def test_existing_buy_order_and_new_sell_order(self):
        agent = self.agents[0]
        agent.execute_action()  # Agent creates a buy order

        # Now, the agent will try to place a sell order
        sell_order = Order(good="socks", price=10, quantity=-5)
        self.marketplace.process_action(agent, sell_order)

        # After placing the sell order, the buy order should be removed, and only the sell order should exist
        self.assertEqual(len(self.marketplace["socks"].buy_orders), 0)
        self.assertEqual(len(self.marketplace["socks"].sell_orders), 1)


class TestAgentInteractions(unittest.TestCase):

    def setUp(self):
        # Setup the environment
        self.environment = Environment()

        # Create two DummyAgents to act as the buyer and seller
        self.buyer = DummyAgent("Buyer")
        self.seller = DummyAgent("Seller")
        self.environment.add(self.buyer)
        self.environment.add(self.seller)

        # Add a Marketplace to the environment
        self.marketplace = Marketplace()
        self.marketplace.create_market("socks")
        self.environment.add(self.marketplace)

        self.environment.prepare()

    def test_trade_execution(self):
        # Initial order: buyer wants 5 socks for $10 each
        buy_order = Order(good="socks", price=10, quantity=5)
        self.marketplace.process_action(self.buyer, buy_order)

        # Seller sells 5 socks for $10 each
        sell_order = Order(good="socks", price=10, quantity=-5)
        self.marketplace.process_action(self.seller, sell_order)

        # Check that trade happened correctly
        self.assertEqual(self.buyer.get_inventory("capital"), 950)  # 1000 - 5*10
        self.assertEqual(self.buyer.get_inventory("socks"), 105)    # 100 + 5
        self.assertEqual(self.seller.get_inventory("capital"), 1050) # 1000 + 5*10
        self.assertEqual(self.seller.get_inventory("socks"), 95)    # 100 - 5

    def test_order_removal_after_trade(self):
        # ... Similar setup as above, then:
        self.assertEqual(len(self.marketplace["socks"].buy_orders), 0)
        self.assertEqual(len(self.marketplace["socks"].sell_orders), 0)

    def test_mismatched_quantities(self):
        # Buyer wants to buy 10 socks for $10 each
        buy_order = Order(good="socks", price=10, quantity=10)
        self.marketplace.process_action(self.buyer, buy_order)

        # Seller only sells 5 socks for $10 each
        sell_order = Order(good="socks", price=10, quantity=-5)
        self.marketplace.process_action(self.seller, sell_order)

        # Check that only 5 socks were traded
        self.assertEqual(self.buyer.get_inventory("capital"), 950)  # 1000 - 5*10
        self.assertEqual(self.buyer.get_inventory("socks"), 105)    # 100 + 5
        self.assertEqual(self.seller.get_inventory("capital"), 1050) # 1000 + 5*10
        self.assertEqual(self.seller.get_inventory("socks"), 95)    # 100 - 5

        # Check that the unmatched part of the buyer's order is still in the order book
        self.assertEqual(len(self.marketplace["socks"].buy_orders), 1)
        self.assertEqual(self.marketplace["socks"].buy_orders[0].quantity, 5)  # Remaining 5 from the initial 10


class TestRandomizedMarketplaceTransactions(unittest.TestCase):

    def test_randomized_trades(self):
        environment = Environment()
        agents = [Agent(f"Agent_{i}") for i in range(10)]
        for agent in agents:
            starting_capital = random.randint(500, 1500)
            starting_socks = random.randint(50, 150)
            agent.inventory.set_starting_inventory({"capital": starting_capital, "socks": starting_socks})
            environment.add(agent)

        marketplace = Marketplace()
        marketplace.create_market("socks")
        environment.add(marketplace)
        environment.prepare()

        total_initial_capital = sum(agent.get_inventory("capital") for agent in agents)
        total_initial_socks = sum(agent.get_inventory("socks") for agent in agents)

        # Generate random trades
        for _ in range(100):
            buyer = random.choice(agents)
            seller = random.choice(agents)
            while seller == buyer:
                seller = random.choice(agents)  # Ensure different agents

            price = random.randint(5, 15)
            quantity = random.randint(1, 10)

            # Create and process buy order
            buy_order = Order(good="socks", price=price, quantity=quantity)
            marketplace.process_action(buyer, buy_order)

            # Create and process sell order
            sell_order = Order(good="socks", price=price, quantity=-quantity)
            marketplace.process_action(seller, sell_order)

        # Assertions
        for agent in agents:
            self.assertGreaterEqual(agent.get_inventory("capital"), 0)
            self.assertGreaterEqual(agent.get_inventory("socks"), 0)

        self.assertEqual(sum(agent.get_inventory("capital") for agent in agents), total_initial_capital)
        self.assertEqual(sum(agent.get_inventory("socks") for agent in agents), total_initial_socks)


class TestMarketplaceStressTest(unittest.TestCase):

    def setUp(self):
        self.environment = Environment(gui=False)
        self.agents = [Agent(f"Agent_{i}") for i in range(50)]  # Use a larger number of agents to stress test
        for agent in self.agents:
            starting_capital = random.randint(500, 1500)
            starting_socks = random.randint(50, 150)
            agent.inventory.set_starting_inventory({"capital": starting_capital, "socks": starting_socks})
            self.environment.add(agent)

        self.marketplace = Marketplace()
        self.marketplace.create_market("socks")
        self.environment.add(self.marketplace)
        self.environment.prepare()

        self.total_initial_capital = sum(agent.get_inventory("capital") for agent in self.agents)
        self.total_initial_socks = sum(agent.get_inventory("socks") for agent in self.agents)

    def test_stress_marketplace(self, depth=2):

        # Randomized trades
        for _ in range(500):  # For added stress
            agent = random.choice(self.agents)
            price = random.randint(5, 15)
            quantity = random.choice([random.randint(1, 10), -random.randint(1, 10)])

            order = Order(good="socks", price=price, quantity=quantity)
            self.marketplace.process_action(agent, order)

        # Edge Cases
        # 1. Zero quantity orders
        zero_order = Order(good="socks", price=10, quantity=0)
        self.marketplace.process_action(random.choice(self.agents), zero_order)

        # 2. Orders that exceed an agent's inventory/capital
        agent = random.choice(self.agents)
        high_price_order = Order(good="socks", price=agent.get_inventory("capital") + 1, quantity=1)
        self.marketplace.process_action(agent, high_price_order)

        high_quantity_order = Order(good="socks", price=10, quantity=agent.get_inventory("socks") + 1)
        self.marketplace.process_action(agent, high_quantity_order)

        # 3. Simultaneous orders from multiple agents
        if depth > 0:
            self.test_stress_marketplace(depth=depth - 1)  # Recursively issue a bunch of random trades with reduced depth

        # Assertions
        for agent in self.agents:
            self.assertGreaterEqual(agent.get_inventory("capital"), 0)
            self.assertGreaterEqual(agent.get_inventory("socks"), 0)

        self.assertEqual(sum(agent.get_inventory("capital") for agent in self.agents), self.total_initial_capital)
        self.assertEqual(sum(agent.get_inventory("socks") for agent in self.agents), self.total_initial_socks)


if __name__ == '__main__':
    unittest.main()
