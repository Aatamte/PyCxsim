from CAES.src.core import Agent, Environment, Query
from CAES.src.core import Order, Dialogue, Marketplace
from CAES.src.agents.language_model_agents.openai_agent import OAIAgent
from CAES.src.agents.population import Population
from CAES.src.agents.agent import ActionRestriction
import numpy as np
import openai
import os


class MyAgent(OAIAgent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.starting_inventory = {
            "capital": 10000,
            "socks": 10,
        }

    def execute_query(self):
        return Query()


def buy_restriction(order: Order):
    if order.quantity >= 0:
        return True
    else:
        return False


def sell_restriction(order: Order):
    if order.quantity <= 0:
        return True
    else:
        return False


if __name__ == '__main__':
    openai.api_key = os.environ["open_ai_key"]

    env = Environment(visualization=True)

    buyer_restrictions = [
        ActionRestriction(
            action=Order,
            func=buy_restriction,
            message_to_agent_on_trigger="You are a buyer, and cannot sell goods, please have a quantity greater than or equal to 1",
            inform_agent_and_retry_action=True,
            max_retries=1
        )
    ]

    seller_restrictions = [
        ActionRestriction(
            action=Order,
            func=sell_restriction,
            message_to_agent_on_trigger="You are a seller, and cannot buy goods",
            inform_agent_and_retry_action=True
        )
    ]

    buyer_population = Population(
        agent=MyAgent(),
        number_of_agents=1,
        action_restrictions=buyer_restrictions
    )

    seller_population = Population(
        agent=MyAgent(),
        number_of_agents=1,
        action_restrictions=seller_restrictions
    )

    env.add(buyer_population)
    env.add(seller_population)

    marketplace = Marketplace()

    print(marketplace.get_action_space(), marketplace.get_query_space())

    env.add(marketplace)

    env.step_delay = 1

    env.max_episodes = 1
    env.max_steps = 50

    # set up the environment
    env.set_up()

    print(env.action_space, env.query_space)

    env.run()

