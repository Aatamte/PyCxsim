from typing import Dict
from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import Union

from src.caes.agents.agent import Agent
from src.caes.artifacts.artifact import Artifact
from src.caes.prompts.prompt import Prompt
from src.caes.queries.query import Query
from src.caes.environment.event import Event


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
    good: str
    price: int
    quantity: int


@dataclass
class MarketPlaceTransaction(Event):
    seller_agent: Agent
    buyer_agent: Agent
    good: str
    quantity: int
    price: int


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
    def __init__(self, product_name: str, environment):
        self.product_name = product_name
        self.environment = environment
        # Initialize lists to hold buy and sell orders
        self.sell_orders = []
        self.buy_orders = []
        self.highest_bid_order: Order = Order(self.product_name, -np.inf, 1)
        self.lowest_offer_order: Order = Order(self.product_name, np.inf, -1)
        self.order_count = 0
        self.num_transactions = 0
        # store transaction history in a pandas DataFrame for easy data manipulation and analysis
        self.history = pd.DataFrame(columns=["transaction_id", "price", "quantity", "buying_agent", "selling_agent"])

        self.best_bid_history = []
        self.best_ask_history = []

        self.event_history = []

    def reset(self):
        # Clear orders
        self.sell_orders = []
        self.buy_orders = []
        # Reset bid/offer orders
        self.highest_bid_order: Order = Order(self.product_name, -np.inf, 1)
        self.lowest_offer_order: Order = Order(self.product_name, np.inf, -1)
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
        if is_buy_order and order.agent.get_amounts("capital") >= order.price:
            return True
        if not is_buy_order and order.agent.get_amounts(self.product_name) >= abs(order.quantity):
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
            self.environment.item_handler.trade(
                incoming_order.agent,
                ("capital", transaction_price),
                book_order.agent,
                (self.product_name, transaction_quantity)
            )

            self.sell_orders.remove(book_order)

            self.event_history.append(
                MarketPlaceTransaction(
                    buyer_agent=incoming_order.agent,
                    seller_agent = book_order.agent,
                    good = self.product_name,
                    quantity = transaction_quantity,
                    price=transaction_price,
                    step=0
                )
            )
        else:
            self.environment.item_handler.trade(
                incoming_order.agent,
                (self.product_name, transaction_quantity),
                book_order.agent,
                ("capital", transaction_price),
            )

            self.buy_orders.remove(book_order)

            self.event_history.append(
                MarketPlaceTransaction(
                    buyer_agent=book_order.agent,
                    seller_agent=incoming_order.agent,
                    good=self.product_name,
                    quantity=transaction_quantity,
                    price=transaction_price,
                    step=0
                )
            )

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

    def step(self):
        self.best_bid_history.append(
            self.highest_bid_order.price
        )
        self.best_ask_history.append(
            self.lowest_offer_order.price
        )

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


class Marketplace(Artifact):
    def __init__(self, infer_from_agents:  bool = True):
        super(Marketplace, self).__init__("Marketplace")
        self.markets: Dict[str, OrderBook] = {}

        self.action_space.append(Order)

        self.query_space.append(Query)

    def process_action(self, agent, action: Union[list, Order]):
        if isinstance(action, tuple):
            market = action[0]
            self.markets[market].add(Order(market, action[1], action[2], agent))
        elif isinstance(action, Order):
            market = action.good
            self.markets[market].add(action)
        elif isinstance(action, list):
            raise TypeError("action should be a tuple, not a list.")
        else:
            raise TypeError("action should either be a ")

    def process_query(self, agent, query):
        observation = ""
        for m in self.markets.values():
            observation += m.product_name + "\n"
            highest_bid = m.highest_bid_order if m.highest_bid_order.price != -np.inf else None
            lowest_offer = m.lowest_offer_order if m.lowest_offer_order.price != np.inf else None

            observation += "Lowest ask order: " + str(lowest_offer) + "\n"
            observation += "highest bid order: " + str(highest_bid)
        return observation

    def step(self):
        for name, market in self.markets.items():
            market.step()

    def set_up(self, environment):
        self.system_prompt = Prompt(
            f"""This is a marketplace where agents can buy and sell goods. A positive quantity represents a buy order, while a negative quantity represents a sell order. If there are no other orders in the marketplace, you are required to submit an order (you may choose parameters that are unrealistic, but valid)"""
        )

    def reset(self, environment):
        for agent in environment.agents:
            for good in agent.inventory.keys():
                if good == "capital":
                    pass
                elif good not in self.markets.keys():
                    self.markets[good] = OrderBook(good, self.environment)

        for market in self.markets.values():
            market.reset()

    def language_model_starting_prompt(self):
        return """Marketplace: allows agents in the simulation to make trades with each other """

    def __getitem__(self, item):
        if item not in self.markets.keys():
            raise KeyError(f"Market {item} is not in {list(self.markets.keys())}")
        return self.markets[item]

    def __repr__(self):
        newline = '\n'
        return \
f"""
MarketPlace
{newline.join([str(orderbook) for market, orderbook in self.markets.items()])}
"""
