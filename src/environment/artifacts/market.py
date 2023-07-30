from typing import Dict
from dataclasses import dataclass
import numpy as np
import pandas as pd
import random
from typing import  Union, Optional

from src.core import Agent
from src.environment.artifacts.artifact import Artifact, AdjacencyMatrix


# An Order is represented as a dataclass for simplicity and ease of use
@dataclass
class Order:
    """
    Represents a single order in the order book.

    Attributes:
    price: The price of the order.
    quantity: The quantity of the order.
    agent: The agent placing the order.
    id: The order id, None by default.
    duration: The order duration, None by default.
    """
    price: int
    quantity: int
    agent: Agent
    id: int = None


# The OrderBook class represents the order book in a market
class OrderBook:
    """
    Represents the order book in a market.

    Attributes:
    product_name: The name of the product being traded in this order book.
    sell_orders: List of all current sell orders.
    buy_orders: List of all current buy orders.
    highest_bid_order: Order with the highest bid.
    lowest_offer_order: Order with the lowest offer.
    order_count: Counts the total number of orders.
    num_transactions: Counts the total number of transactions.
    history: A DataFrame to store history of transactions.
    """
    def __init__(self, product_name: str):
        self.product_name = product_name
        # Initialize lists to hold buy and sell orders
        self.sell_orders = []
        self.buy_orders = []
        self.highest_bid_order: Order = Order(-np.inf, 1, Agent())
        self.lowest_offer_order: Order = Order(np.inf, -1, Agent())
        self.order_count = 0
        self.num_transactions = 0
        # store transaction history in a pandas DataFrame for easy data manipulation and analysis
        self.history = pd.DataFrame(columns=["transaction_id", "price", "quantity", "buying_agent", "selling_agent"])

    def reset(self):
        # Clear orders
        self.sell_orders = []
        self.buy_orders = []
        # Reset bid/offer orders
        self.highest_bid_order: Order = Order(-np.inf, 1, Agent())
        self.lowest_offer_order: Order = Order(np.inf, -1, Agent())
        # Reset counters
        self.order_count = 0
        self.num_transactions = 0
        # Reset history DataFrame
        self.history = pd.DataFrame(
            columns=["transaction_id", "price", "quantity", "buyer", "seller"]
        )

    def _can_order_be_executed(self, order: Order, is_buy_order: bool) -> bool:
        if not isinstance(order, Order):
            raise TypeError("order should be of type <Order>")
        # no matching order exists in the order book
        if (is_buy_order and len(self.sell_orders) == 0) or (not is_buy_order and len(self.buy_orders) == 0):
            return False
        # orders exist in order book
        else:
            if is_buy_order and (order.price >= self.lowest_offer_order.price):
                return self.execute(order, self.lowest_offer_order)
            if not is_buy_order and (order.price <= self.highest_bid_order.price):
                return self.execute(order, self.highest_bid_order)
        return False

    def is_order_legitimate(self, order: Order, is_buy_order: bool):
        if order.quantity == 0:
            return False
        # if agent is buying,
        if is_buy_order and order.agent.capital >= order.price:
            return True
        if not is_buy_order and order.agent.inventory[self.product_name] >= abs(order.quantity):
            return True
        return False

    def should_remove_existing_order(self, order: Order):
        for existing_order in self.sell_orders:
            if existing_order.agent == order.agent:
                self.sell_orders.remove(existing_order)
        for existing_order in self.buy_orders:
            if existing_order.agent == order.agent:
                self.buy_orders.remove(existing_order)

    def add(self, order: Order):
        order.id = self.order_count
        self.order_count += 1

        # check if agent has enough capital or quantity of good to make the order
        is_buy_order = True if order.quantity >= 0 else False
        order_is_legitimate = self.is_order_legitimate(order, is_buy_order)
        self.should_remove_existing_order(order)

        if order_is_legitimate:
            # if order can be executed immediately, do it
            order_was_executed = self._can_order_be_executed(order, is_buy_order)

            if not order_was_executed:
                if is_buy_order:
                    self.buy_orders.append(order)
                else:
                    self.sell_orders.append(order)

            if len(self.buy_orders) != 0:
                self.buy_orders = sorted(self.buy_orders, key=lambda x: x.price, reverse=True)
                self.highest_bid_order = self.buy_orders[0]

            if len(self.sell_orders) != 0:
                self.sell_orders = sorted(self.sell_orders, key=lambda x: x.price)
                self.lowest_offer_order = self.sell_orders[0]

    def execute(self, incoming_order: Order, book_order: Order):
        transaction_price = book_order.price
        is_incoming_buy_order = True if incoming_order.quantity >= 0 else False
        transaction_quantity = min(abs(incoming_order.quantity), abs(book_order.quantity))

        if is_incoming_buy_order:
            incoming_order.agent.inventory[self.product_name] += transaction_quantity
            book_order.agent.inventory[self.product_name] -= transaction_quantity

            incoming_order.agent.capital -= transaction_price
            book_order.agent.capital += transaction_price

            # modify orders to reflect transaction
            incoming_order.quantity -= transaction_quantity
            book_order.quantity += transaction_quantity

            if book_order.quantity == 0:
                self.sell_orders.remove(book_order)

        else:
            incoming_order.agent.inventory[self.product_name] -= transaction_quantity
            book_order.agent.inventory[self.product_name] += transaction_quantity

            incoming_order.agent.capital += transaction_price
            book_order.agent.capital -= transaction_price

            # modify orders to reflect transaction
            incoming_order.quantity += transaction_quantity
            book_order.quantity -= transaction_quantity

            if book_order.quantity == 0:
                self.buy_orders.remove(book_order)

        self.history = pd.concat([self.history, pd.DataFrame(
            {
                "transaction_id": [self.num_transactions],
                "price": [transaction_price],
                "quantity": [transaction_quantity],
                "buyer": [incoming_order.agent.name if is_incoming_buy_order else book_order.agent.name],
                "seller": [incoming_order.agent.name if not is_incoming_buy_order else book_order.agent.name]
            })]
                                            )
        self.num_transactions += 1
        return True

    def get_full_orderbook(self):
        return [(order.price, order.quantity) for order in self.buy_orders] + [(order.price, order.quantity) for order in self.sell_orders]

    def get_buyers(self):
        return [str(order.price) for order in self.buy_orders]

    def get_sellers(self):
        return [str(order.price) for order in self.sell_orders]

    def __repr__(self):
        new_line = "\n"
        sell_order_list = [str((order.price, order.quantity, order.agent.name, order.id)) for order in self.sell_orders]
        buy_order_list = [str((order.price, order.quantity, order.agent.name, order.id)) for order in self.buy_orders][
                         ::-1]
        return \
f"""===================================
{self.product_name} Order Book
(price, quantity, name)
{new_line.join(map(str, sell_order_list))}
{new_line.join(map(str, buy_order_list))}
==================================="""


class Market(Artifact):
    """
    Represents a market in the simulation. Inherits from Artifact.

    Attributes:
    market_name: The name of the market.
    market: An OrderBook object representing the order book for this market.
    """
    def __init__(self, market_name):
        super(Market, self).__init__("Market")
        self.market_name = market_name
        self.market = OrderBook(self.market_name)
        self.agents = []
        self.transaction_adjacency_matrix = None
        self.agent_name_lookup = None

    # The execute method adds an order to the market's order book
    def execute(self, agent, action: Union[list, Order]):
        if isinstance(action, tuple):
            self.market.add(Order(action[1], action[2], agent))
        elif isinstance(action, Order):
            self.market.add(action)
        elif isinstance(action, list):
            raise TypeError("action should be a tuple, not a list.")
        else:
            raise TypeError("action should either be a ")

    # The generate_observations method prepares the current market state for all agents
    def generate_observations(self, agents):
        self.agents = agents
        observations = {agent.name: (self.market.product_name, self.market.get_full_orderbook()) for agent in agents}
        return observations

    # Reset the market by resetting its order book
    def reset(self, environment):
        """
        Resets the order book. Clears all orders, resets bid/offer orders and resets counters.
        """
        self.market.reset()
        self.agents = environment.agents
        self.agent_name_lookup = environment.agent_name_lookup
        self.transaction_adjacency_matrix = AdjacencyMatrix(self.agents)

    def get_adjacency_matrix(self):
        size = len(self.agents)
        mat = [[random.randint(0, 0) for _ in range(size)] for _ in range(size)]
        for link in self.market.history[["buyer", "seller"]].values[-10:]:
            source_idx = self.agent_name_lookup[link[0]].id
            sink_idx = self.agent_name_lookup[link[1]].id
            mat[source_idx][sink_idx] = 1
            #mat[sink_idx][source_idx] = 1
        return mat

    def history(self):
        return self.market.history

    def __repr__(self):
        return str(self.market)


class Marketplace(Artifact):
    def __init__(self, market_names: list = None):
        super(Marketplace, self).__init__("Marketplace")
        self.markets: Dict[str, OrderBook] = {market_name: OrderBook(market_name) for market_name in market_names} if market_names else None

    def execute(self, agent, action: tuple):
        self.markets[action[0]].add(Order(action[1], action[2], agent))

    def generate_observations(self, agents):
        observations = {agent.name: [(m.product_name, m.get_full_orderbook()) for m in self.markets.values()] for agent in agents}
        return observations

    def reset(self):
        for market in self.markets.values():
            market.reset()

    def __repr__(self):
        newline = '\n'
        return \
f"""
MarketPlace
{newline.join([str(orderbook) for market, orderbook in self.markets.items()])}
"""


if __name__ == '__main__':
    buy_agent = Agent("John")
    sell_agent = Agent("Gary")

    buy_agent.inventory.starting_capital = 1000
    sell_agent.inventory.starting_capital = 1000

    buy_agent.reset()
    sell_agent.reset()

    buy_agent.inventory["socks"] = 0
    sell_agent.inventory["socks"] = 10

    OB = OrderBook("socks")
    order_one = Order(price=90, quantity=1, agent=buy_agent)
    order_two = Order(price=100, quantity=-1, agent=sell_agent)
    order_three = Order(price=105, quantity=1, agent=buy_agent)
    order_four = Order(price=110, quantity=-1, agent=sell_agent)

    for r_int in range(100):
        buy = np.random.randint(0, 2)
        p = int(np.random.normal(100, 15, 1)[0])
        q = np.random.randint(1, 2)
        if buy:
            OB.add(Order(
                price=p,
                quantity=q,
                agent=buy_agent
            ))
        else:
            OB.add(
                Order(
                    price=p,
                    quantity=-q,
                    agent=sell_agent
                )
            )
        print(r_int)
        print(OB)
        print(OB.order_book_history)
        print(sell_agent.inventory)

    # print(
    #    buy_agent.capital,
    #    buy_agent.inventory,
    #    sell_agent.capital,
    #    sell_agent.inventory
    # )
