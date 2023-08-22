import numpy as np
from src.CAES import Agent, Item
from collections import deque


class ItemGenerator:
    def __init__(self, agents):
        self.agents = agents
        self.item_counts = {}

    def generate_agent_items(self):
        for agent in self.agents:
            for item in agent.inventory.keys():
                amount_needed = agent[item]
                agent.inventory[item] = deque()
                #
                if item not in self.item_counts:
                    self.item_counts[item] = 0

                #
                for needed_items in range(amount_needed):
                    self.item_counts[item] += 1
                    agent.inventory[item].append(Item(name=item, uid=self.item_counts[item]))

    def generate_new_item(self, name, amount: int):
        pass


class MyAgent(Agent):
    def __init__(self):
        super(MyAgent, self).__init__()
        self.inventory = {
            "capital": 50,
            "socks": 10
        }

        self.is_buyer = True if np.random.randint(0, 100) > 50 else False
        self.quantity = 1 if self.is_buyer else -1

    def select_action(self):
        if self.is_buyer:
            price = np.random.randint(85, 100)
        else:
            price = np.random.randint(90, 105)

        if np.random.randint(0, 100) > 50:
            self.action_queue.append(("Market", ("socks", price, self.quantity)))
        else:
            self.action_queue.append(None)


if __name__ == '__main__':
    agents = [MyAgent() for _ in range(10)]

    item_manager = ItemGenerator(agents)

    item_manager.generate_agent_items()

    agent_one = agents[0]
    agent_two = agents[1]

    agent_one += Item(name="capital", uid=20)

    agent_one.trade(
        ("capital", 20),
        ("socks", 1),
        agent_two
    )

    print(agent_one.get_amounts("capital"))
    print(agent_two.get_amounts("capital"))
    print(agent_one.get_amounts("socks"))
    print(agent_two.get_amounts("socks"))









