import unittest
import pandas as pd
from src.caes import Order, Agent  # Import the necessary classes
from src.caes.artifacts.marketplace import OrderBook


class TestOrderBook(unittest.TestCase):

    def setUp(self):
        self.env = None  # Mock your environment if needed
        self.book = OrderBook("apple", self.env)
        self.agent = Agent() # Initialize as necessary
        self.agent.starting_inventory = {"capital": 1000, "apple": 100}
        self.agent.set_up()
        self.order = Order("apple", 100, 1, self.agent)

    def test_init(self):
        self.assertEqual(self.book.product_name, "apple")
        self.assertEqual(self.book.sell_orders, [])
        self.assertEqual(self.book.buy_orders, [])
        self.assertIsInstance(self.book.highest_bid_order, Order)
        self.assertIsInstance(self.book.lowest_offer_order, Order)
        self.assertEqual(self.book.order_count, 0)
        self.assertEqual(self.book.num_transactions, 0)
        self.assertIsInstance(self.book.history, pd.DataFrame)

    def test_reset(self):
        self.book.reset()
        self.assertEqual(self.book.sell_orders, [])
        self.assertEqual(self.book.buy_orders, [])
        self.assertEqual(self.book.order_count, 0)
        self.assertEqual(self.book.num_transactions, 0)
        self.assertIsInstance(self.book.history, pd.DataFrame)

    def test_can_order_be_executed(self):
        # No matching order exists in the order book
        self.assertFalse(self.book._can_order_be_executed(self.order, True))

        # Orders exist in the order book
        self.book.sell_orders.append(Order("apple", 90, -1, self.agent))
        self.assertTrue(self.book._can_order_be_executed(self.order, True))

    def test_is_order_legitimate(self):
        # Assuming agent has infinite capital
        self.assertTrue(self.book.is_order_legitimate(self.order, True))

        # Assuming agent has zero capital
        # Mock the get_amounts method on the agent to return 0 for this test
        self.agent.get_amounts = lambda item: 0
        self.assertFalse(self.book.is_order_legitimate(self.order, True))


    def test_should_remove_existing_order(self):
        self.book.sell_orders.append(self.order)
        self.book.should_remove_existing_order(self.order)
        self.assertNotIn(self.order, self.book.sell_orders)

    def test_add(self):
        initial_count = self.book.order_count
        self.book.add(self.order)
        self.assertEqual(self.book.order_count, initial_count + 1)

    def test_execute(self):
        buy_order = Order("apple", 100, 10, Agent())
        sell_order = Order("apple", 90, -10, Agent())

        self.book.add(buy_order)
        self.book.add(sell_order)

        initial_transactions = self.book.num_transactions
        self.book.execute(buy_order, sell_order)
        self.assertEqual(self.book.num_transactions, initial_transactions + 1)

    def test_step(self):
        self.book.step()
        self.assertIn(self.book.highest_bid_order.price, self.book.best_bid_history)
        self.assertIn(self.book.lowest_offer_order.price, self.book.best_ask_history)

    def test_get_full_orderbook(self):
        self.book.add(self.order)
        full_orderbook = self.book.get_full_orderbook()
        self.assertIn((self.order.price, self.order.quantity), full_orderbook)


if __name__ == "__main__":
    unittest.main()
