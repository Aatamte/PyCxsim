import unittest
import pandas as pd
from src.cxsim import Agent  # Import the necessary classes
from src.cxsim.artifacts.marketplace import OrderBook, Order


class TestOrderBook(unittest.TestCase):

    def setUp(self):
        self.env = None  # Mock your environment if needed
        self.book = OrderBook("apple", self.env)

    def test_step(self):
        self.book.step()
        self.assertIn(self.book.highest_bid_order.price, self.book.best_bid_history)
        self.assertIn(self.book.lowest_offer_order.price, self.book.best_ask_history)


if __name__ == "__main__":
    unittest.main()
