from typing import Dict
from dataclasses import dataclass
import numpy as np
import pandas as pd

from src.core import BaseAgent
from src.environment.artifacts.artifact import Artifact


@dataclass
class Order:
    price: int
    quantity: int
    agent: BaseAgent
    id: int = None
    duration: int = None


class OrderBook(Artifact):
    """
    OrderBook is a class that allows agents to trade with each other
    """

    def __init__(self, product_name):
        super().__init__()
        self.product_name = product_name
        self.sell_orders = []
        self.buy_orders = []
        self.highest_bid_order: Order = Order(-np.inf, 1, BaseAgent())
        self.lowest_offer_order: Order = Order(np.inf, -1, BaseAgent())
        self.order_count = 0
        self.num_transactions = 0
        self.history = pd.DataFrame(columns=["transaction_id", "price", "quantity", "buying_agent", "selling_agent"])

    def reset(self):
        self.sell_orders = []
        self.buy_orders = []
        self.highest_bid_order: Order = Order(-np.inf, 1, BaseAgent())
        self.lowest_offer_order: Order = Order(np.inf, -1, BaseAgent())
        self.order_count = 0
        self.num_transactions = 0
        self.history = pd.DataFrame(
            columns=["transaction_id", "price", "quantity", "buying_agent", "selling_agent"]
        )

    def _can_order_be_executed(self, order: Order, is_buy_order: bool) -> bool:
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
        if is_buy_order and order.agent.inventory.capital >= order.price:
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

            incoming_order.agent.inventory.capital -= transaction_price
            book_order.agent.inventory.capital += transaction_price

            # modify orders to reflect transaction
            incoming_order.quantity -= transaction_quantity
            book_order.quantity += transaction_quantity

            if book_order.quantity == 0:
                self.sell_orders.remove(book_order)

        else:
            incoming_order.agent.inventory[self.product_name] -= transaction_quantity
            book_order.agent.inventory[self.product_name] += transaction_quantity

            incoming_order.agent.inventory.capital += transaction_price
            book_order.agent.inventory.capital -= transaction_price

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
                "buying_agent": [incoming_order.agent.name if is_incoming_buy_order else book_order.agent.name],
                "selling_agent": [incoming_order.agent.name if not is_incoming_buy_order else book_order.agent.name]
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


class Marketplace:
    def __init__(self, market_names: list = None):
        self.name = "MarketPlace"
        self.markets: Dict[str, OrderBook] = {market_name: OrderBook(market_name) for market_name in market_names} if market_names else None

    def step(self, agent, action: tuple):
        market_name = action[0]
        price = action[1]
        quantity = action[2]
        print(action)

        self.markets[market_name].add(Order(price, quantity, agent))
        print(self.markets)

    def describe(self):
        print("Actions take the form of ('market name', order)")

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
    buy_agent = BaseAgent("John")
    sell_agent = BaseAgent("Gary")

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
