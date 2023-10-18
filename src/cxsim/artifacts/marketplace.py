from abc import ABC
from typing import Dict
import pandas as pd
from typing import Union
from dataclasses import dataclass, field, fields

from cxsim.agents.agent import Agent
from cxsim.artifacts.artifact import Artifact
from cxsim.environment.event import Event


@dataclass
class BuyOrder:
    """
    Represents a single buy order in the order book
    """
    good: str
    price: int
    quantity: int


@dataclass
class SellOrder:
    """
    Represents a single sell order in the order book
    """
    good: str = field(metadata={"description": "The name of the good being sold"})
    price: int = field(metadata={"description": "The selling price of the good"})
    quantity: int = field(metadata={"description": "The quantity of the good being sold"})


@dataclass
class MarketPlaceQuery:
    """
    Retrieves the market information for a single good.
    good [str]: name of the good
    """
    good: str


@dataclass
class MarketPlaceTransaction(Event):
    seller_agent: Agent
    buyer_agent: Agent
    good: str
    quantity: int
    price: int


@dataclass
class InternalOrder:
    good: str
    price: int
    quantity: int
    agent: None

    def __eq__(self, other):
        if isinstance(other, InternalOrder):
            return (self.good == other.good and
                    self.price == other.price and
                    self.quantity == other.quantity and
                    self.agent == other.agent)
        return False


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
        self.highest_bid_order = None
        self.lowest_offer_order = None
        self.order_count = 0
        self.num_transactions = 0
        # store transaction history in a pandas DataFrame for easy data manipulation and analysis
        self.history = pd.DataFrame(columns=["transaction_id", "price", "quantity", "buying_agent", "selling_agent"])

        self.best_bid_history = []
        self.best_ask_history = []

        self.event_history = []

        self.order_history = []

    def reset(self):
        # Clear orders
        self.sell_orders = []
        self.buy_orders = []
        # Reset bid/offer orders
        self.highest_bid_order = None
        self.lowest_offer_order = None
        # Reset counters
        self.order_count = 0
        self.num_transactions = 0
        # Reset history DataFrame
        self.history = pd.DataFrame(
            columns=["transaction_id", "price", "quantity", "buyer", "seller"]
        )

    def _can_order_be_executed(self, order: InternalOrder, is_buy_order: bool) -> bool:
        if not isinstance(order, InternalOrder):
            raise TypeError("order should be of type <InternalOrder>")
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

    def is_order_legitimate(self, order: InternalOrder, is_buy_order: bool):
        # If the order quantity is zero, it's invalid
        if order.quantity == 0:
            return False

        if order.price <= 0:
            return False

        # Check for an existing order from the same agent in the opposite direction
        if is_buy_order:
            existing_order_cost = sum([o.price for o in self.buy_orders if o.agent == order.agent])
            total_order_cost = order.price + existing_order_cost

            if order.agent.get_inventory("capital") < total_order_cost:
                return False

            for existing_order in self.sell_orders:
                if existing_order.agent == order.agent:
                    # Remove the existing sell order
                    self.sell_orders.remove(existing_order)
                    return True

        else:
            existing_goods_quantity = sum([abs(o.quantity) for o in self.sell_orders if o.agent == order.agent])
            total_goods_quantity = abs(order.quantity) + existing_goods_quantity

            if order.agent.get_inventory(self.product_name) < total_goods_quantity:
                return False

            for existing_order in self.buy_orders:
                if existing_order.agent == order.agent:
                    # Remove the existing buy order
                    self.buy_orders.remove(existing_order)
                    return True

        if is_buy_order:
            total_buy_value = sum([o.price * o.quantity for o in self.buy_orders if o.agent == order.agent])
            assert order.agent.get_inventory(
                "capital") >= total_buy_value, "Agent doesn't have enough capital for all buy orders."
        else:
            total_sell_qty = sum([abs(o.quantity) for o in self.sell_orders if o.agent == order.agent])
            assert order.agent.get_inventory(
                self.product_name) >= total_sell_qty, "Agent doesn't have enough inventory for all sell orders."

        # Usual legitimacy checks
        if is_buy_order:
            return order.agent.get_inventory("capital") >= order.price
        else:
            return order.agent.get_inventory(self.product_name) >= abs(order.quantity)

    def update_best_orders(self):
        if len(self.buy_orders) != 0:
            self.buy_orders = sorted(self.buy_orders, key=lambda x: x.price, reverse=True)
            self.highest_bid_order = self.buy_orders[0]
        else:
            self.highest_bid_order = None

        if len(self.sell_orders) != 0:
            self.sell_orders = sorted(self.sell_orders, key=lambda x: x.price)
            self.lowest_offer_order = self.sell_orders[0]
        else:
            self.lowest_offer_order = None

    def should_remove_existing_order(self, order: InternalOrder):
        self.sell_orders = [o for o in self.sell_orders if o.agent != order.agent]
        self.buy_orders = [o for o in self.buy_orders if o.agent != order.agent]

        self.update_best_orders()

    def add(self, order: InternalOrder):
        self.order_history.append(order)
        order.id = self.order_count
        self.order_count += 1

        # check if agent has enough capital or quantity of good to make the order
        is_buy_order = True if order.quantity >= 0 else False

        existing_buy_orders = [o for o in self.buy_orders if o.agent == order.agent]
        existing_sell_orders = [o for o in self.sell_orders if o.agent == order.agent]
        assert not (existing_buy_orders and existing_sell_orders), "Agent has orders on both sides of the market."
        self.should_remove_existing_order(order)

        order_is_legitimate = self.is_order_legitimate(order, is_buy_order)

        if order_is_legitimate:
            # if order can be executed immediately, do it
            order_was_executed = self._can_order_be_executed(order, is_buy_order)

            if not order_was_executed:
                if is_buy_order:
                    assert order.quantity > 0, "Buy order with non-positive quantity detected."
                    self.buy_orders.append(order)
                else:
                    assert order.quantity < 0, "Sell order with non-negative quantity detected."
                    self.sell_orders.append(order)

            self.update_best_orders()

            # At the end of the 'add' method, after updating 'highest_bid_order' and 'lowest_offer_order'
            if self.buy_orders and self.highest_bid_order:
                assert self.highest_bid_order == self.buy_orders[0], "highest_bid_order is not consistent with sorted buy_orders."
            if self.sell_orders and self.lowest_offer_order:
                assert self.lowest_offer_order == self.sell_orders[0], "lowest_offer_order is not consistent with sorted sell_orders."

        if self.highest_bid_order:
            self.best_bid_history.append(self.highest_bid_order.price)
        else:
            if self.best_bid_history:
                last_known_bid = self.best_bid_history[-1]
                self.best_bid_history.append(last_known_bid)

        if self.lowest_offer_order:
            self.best_ask_history.append(self.lowest_offer_order.price)
        else:
            if self.best_ask_history:
                last_known_ask = self.best_ask_history[-1]
                self.best_ask_history.append(last_known_ask)

    def execute(self, incoming_order: InternalOrder, book_order: InternalOrder):
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
            self.event_history.append(
                MarketPlaceTransaction(
                    buyer_agent=incoming_order.agent,
                    seller_agent=book_order.agent,
                    good=self.product_name,
                    quantity=transaction_quantity,
                    price=transaction_price,
                )
            )
        else:
            self.environment.item_handler.trade(
                incoming_order.agent,
                (self.product_name, transaction_quantity),
                book_order.agent,
                ("capital", transaction_price),
            )
            self.event_history.append(
                MarketPlaceTransaction(
                    buyer_agent=book_order.agent,
                    seller_agent=incoming_order.agent,
                    good=self.product_name,
                    quantity=transaction_quantity,
                    price=transaction_price,
                )
            )

        # Adjust unmatched parts of the orders for the incoming order
        if abs(incoming_order.quantity) > transaction_quantity:
            # If the incoming order was not fully matched
            incoming_order.quantity -= transaction_quantity if is_incoming_buy_order else -transaction_quantity
        else:
            # If the incoming order was fully matched or exceeded
            if is_incoming_buy_order:
                if incoming_order in self.buy_orders:
                    self.buy_orders.remove(incoming_order)
            else:
                if incoming_order in self.sell_orders:
                    self.sell_orders.remove(incoming_order)

        # Adjust unmatched parts of the orders for the book order
        if abs(book_order.quantity) > transaction_quantity:
            # If the book order was not fully matched
            book_order.quantity -= transaction_quantity if book_order.quantity > 0 else -transaction_quantity
        else:
            # If the book order was fully matched
            if book_order.quantity > 0:
                self.buy_orders.remove(book_order)
            else:
                self.sell_orders.remove(book_order)

        # Update history and transaction counter
        self.history = pd.concat([
            self.history,
            pd.DataFrame({
                "transaction_id": [self.num_transactions],
                "price": [transaction_price],
                "quantity": [transaction_quantity],
                "buyer": [incoming_order.agent.name if is_incoming_buy_order else book_order.agent.name],
                "seller": [incoming_order.agent.name if not is_incoming_buy_order else book_order.agent.name]
            })
        ])
        self.num_transactions += 1

        assert incoming_order not in self.buy_orders, "Executed buy order still present in buy_orders."
        assert incoming_order not in self.sell_orders, "Executed sell order still present in sell_orders."
        self.update_best_orders()
        return True

    def step(self):
        pass

    def get_full_orderbook(self):
        return [(order.price, order.quantity) for order in self.buy_orders] + [(order.price, order.quantity) for order in self.sell_orders]

    def get_buyers(self):
        return [str(order.price) for order in self.buy_orders]

    def get_sellers(self):
        return [str(order.price) for order in self.sell_orders]

    def __repr__(self):
        new_line = "\n"
        sell_order_list = [str((order.price, abs(order.quantity), order.agent.name)) for order in self.sell_orders][:5]
        buy_order_list = [str((order.price, order.quantity, order.agent.name)) for order in self.buy_orders][:5]
        return \
f"""===================================
{self.product_name} Order Book
Sell orders
(price, quantity, name)
{new_line.join(map(str, sell_order_list[::-1]))}
Buy orders
(price, quantity, name)
{new_line.join(map(str, buy_order_list))}
===================================
Last 5 transactions:
{self.history.sort_values(by="transaction_id", ascending=False).head(5)}
"""


class Marketplace(Artifact):
    """
    The marketplace facilitates transactions between agents in the simulation. Prices are in $1 increments
    """
    def __init__(
            self,
            allow_multiple_orders: bool = False,
            product_names = None,
            infer_goods_from_agents:  bool = True
    ):
        super(Marketplace, self).__init__("Marketplace")
        self.infer_goods_from_agents = infer_goods_from_agents
        self.markets: Dict[str, OrderBook] = {}

        if product_names:
            self.market_names = product_names
        else:
            self.market_names = []

        self.action_space.append(BuyOrder)
        self.action_space.append(SellOrder)
        self.action_space.append(MarketPlaceQuery)

    def process_action(self, agent, action: Union[list, BuyOrder, SellOrder]):
        if isinstance(action, MarketPlaceQuery):
            if action.good not in self.markets.keys():
                return f"The good: {action.good}, does not exist in the marketplace"
            else:
                m = self.markets[action.good]
                return m.__repr__()
        else:
            if isinstance(action, tuple):
                market = action[0]
                self.markets[market].add(InternalOrder(market, action[1], action[2], agent))
            elif isinstance(action, BuyOrder):
                market = action.good
                self.markets[market].add(InternalOrder(good=action.good, price=action.price, quantity=action.quantity, agent=agent))
                return "Your Buy Order is in marketplace"
            elif isinstance(action, SellOrder):
                market = action.good
                self.markets[market].add(InternalOrder(good=action.good, price=action.price, quantity=-action.quantity, agent=agent))
                return "Your Sell Order is in marketplace"
            elif isinstance(action, list):
                raise TypeError("action should be a tuple, not a list.")
            else:
                raise TypeError("action should either be a ")

    def step(self):
        for name, market in self.markets.items():
            market.step()

    def set_up(self, environment):
        if self.infer_goods_from_agents:
            for agent in environment.agents:
                for good in agent.inventory.keys():
                    if good == "capital":
                        pass
                    elif good not in self.markets.keys():
                        self.market_names.append(good)

        for market_name in self.market_names:
            self.markets[market_name] = OrderBook(market_name, environment)

    def reset(self, environment):
        for market in self.markets.values():
            market.reset()

    def create_market(self, product_name: str):
        self.market_names.append(product_name)

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
