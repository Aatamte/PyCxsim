from collections import deque
from src.CAES.agents.item import Item


class Inventory:
    def __init__(self):
        self.internal_inventory = {}  # Holds deques of Items
        self.inventory = {}  # Holds integer representations of lengths
        self.starting_inventory = {}
        self.deltas = []

    def add_item(self, item):
        if item.name not in self.internal_inventory:
            self.internal_inventory[item.name] = deque()
        self.internal_inventory[item.name].append(item)
        self.inventory[item.name] = len(self.internal_inventory[item.name])

        # Record the addition in deltas
        self.deltas.append(("add", item.name, item.id))

    def reset(self):
        """Reset the current inventory to the starting inventory."""
        self.internal_inventory = {}
        self.inventory = {}
        for item_name, quantity in self.starting_inventory.items():
            self.internal_inventory[item_name] = deque([Item(item_name) for _ in range(quantity)])
            self.inventory[item_name] = quantity
        self.deltas.clear()  # Clear the deltas

    def set_starting_inventory(self, starting_inventory):
        """Set the starting inventory for the agent."""
        self.starting_inventory = starting_inventory.copy()  # Store a copy of the starting inventory
        for item_name, quantity in starting_inventory.items():
            self.internal_inventory[item_name] = deque([Item(item_name) for _ in range(quantity)])
            self.inventory[item_name] = quantity

    def remove_item(self, item_name):
        if item_name in self.internal_inventory and self.internal_inventory[item_name]:
            removed_item = self.internal_inventory[item_name].popleft()
            self.inventory[item_name] = len(self.internal_inventory[item_name])

            # Record the removal in deltas
            self.deltas.append(("remove", item_name, removed_item.id))
            return removed_item
        return None

    def get_recent_deltas(self, num_deltas=1):
        """Retrieve the most recent changes (deltas) to the inventory."""
        return self.deltas[-num_deltas:]

    def reconstruct_past_state(self, steps_back=1):
        """Reconstruct a past inventory state using deltas."""
        past_state = dict(self.inventory)
        for step in reversed(self.deltas[-steps_back:]):
            action, item_name, item_id = step
            if action == "add":
                past_state[item_name] -= 1
            elif action == "remove":
                past_state[item_name] += 1
        return past_state

    def get_quantity(self, item_name):
        print(item_name, self.inventory)
        return self.inventory.get(item_name, 0)

    def __getitem__(self, item_name):
        """Mimics dictionary get behavior."""
        return self.inventory.get(item_name, 0)

    def __setitem__(self, item_name, item):
        """Mimics dictionary set behavior. Assumes item is an instance of the Item class."""
        if item_name not in self.internal_inventory:
            self.internal_inventory[item_name] = deque()
        self.internal_inventory[item_name].append(item)
        self.inventory[item_name] = len(self.internal_inventory[item_name])

    def __delitem__(self, item_name):
        """Mimics dictionary delete behavior."""
        if item_name in self.internal_inventory:
            self.internal_inventory[item_name].popleft()
            self.inventory[item_name] = len(self.internal_inventory[item_name])

    def keys(self):
        """Mimics dictionary keys method."""
        return self.inventory.keys()

    def values(self):
        """Mimics dictionary values method."""
        return self.inventory.values()

    def items(self):
        """Mimics dictionary items method."""
        return self.inventory.items()

    def get(self, item_name, default=None):
        """Mimics dictionary get method."""
        return self.inventory.get(item_name, default)

    def __repr__(self):
        return str(self.inventory)

