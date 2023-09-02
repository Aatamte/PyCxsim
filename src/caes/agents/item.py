
class Item:
    id_counters = {}  # Dictionary to hold unique ID counters for each item name

    def __init__(self, name):
        self.name = name
        # If the item name is not in the id_counters dictionary, initialize it with 0
        if name not in Item.id_counters:
            Item.id_counters[name] = 0
        # Assign a unique ID to the item and increment the counter for that item name
        self.id = Item.id_counters[name]
        Item.id_counters[name] += 1

    def __repr__(self):
        return f"Item(name={self.name}, id={self.id})"


class ItemHandler:
    def __init__(self, environment):
        self.environment = environment
        self.agents = self.environment.agents
        self.item_counts = {}

    def generate_new_item(self, name, amount: int):
        pass

    @staticmethod
    def trade(agent1, agent1_item: tuple, agent2, agent2_item: tuple):

        """
        Executes a trade between two agents.
        agent1_item and agent2_item are tuples in the format (item_name, quantity).
        If item_name is "capital", the quantity represents the price per item.
        """

        # Handle the case where agent1 is buying items from agent2 using capital
        if agent1_item[0] == "capital":
            total_cost = agent1_item[1] * agent2_item[1]  # price per item * number of items
            if agent1.inventory.get_quantity("capital") >= total_cost:
                for _ in range(agent2_item[1]):
                    item_to_trade = agent2.inventory.remove_item(agent2_item[0])
                    if item_to_trade:  # Ensure the item was successfully removed
                        agent1.inventory.add_item(item_to_trade)
                # Deduct capital from agent1 and add to agent2
                for _ in range(total_cost):
                    capital_to_trade = agent1.inventory.remove_item("capital")
                    if capital_to_trade:
                        agent2.inventory.add_item(capital_to_trade)

        # Handle the case where agent2 is buying items from agent1 using capital
        elif agent2_item[0] == "capital":
            total_cost = agent2_item[1] * agent1_item[1]  # price per item * number of items
            if agent2.inventory.get_quantity("capital") >= total_cost:
                for _ in range(agent1_item[1]):
                    item_to_trade = agent1.inventory.remove_item(agent1_item[0])
                    if item_to_trade:  # Ensure the item was successfully removed
                        agent2.inventory.add_item(item_to_trade)
                # Deduct capital from agent2 and add to agent1
                for _ in range(total_cost):
                    capital_to_trade = agent2.inventory.remove_item("capital")
                    if capital_to_trade:
                        agent1.inventory.add_item(capital_to_trade)

        # Handle the general case where agents are trading items
        else:
            # Transfer items from agent1 to agent2
            for _ in range(agent1_item[1]):
                item_to_trade = agent1.inventory.remove_item(agent1_item[0])
                if item_to_trade:  # Ensure the item was successfully removed
                    agent2.inventory.add_item(item_to_trade)

            # Transfer items from agent2 to agent1
            for _ in range(agent2_item[1]):
                item_to_trade = agent2.inventory.remove_item(agent2_item[0])
                if item_to_trade:  # Ensure the item was successfully removed
                    agent1.inventory.add_item(item_to_trade)
