import unittest
from src.cxsim.agents.traits.inventory import Inventory


class Item:
    id_counter = 0

    def __init__(self, name):
        self.name = name
        self.id = Item.id_counter
        Item.id_counter += 1

# ... [Inventory class definition]


class TestInventory(unittest.TestCase):

    def setUp(self):
        self.inv = Inventory()
        self.apple = Item("apple")
        self.orange = Item("orange")

    def test_add_item(self):
        self.inv.add_item(self.apple)
        self.assertEqual(self.inv.inventory["apple"], 1)
        self.assertEqual(self.inv.internal_inventory["apple"][0], self.apple)

    def test_remove_item(self):
        self.inv.add_item(self.apple)
        removed_item = self.inv.remove_item("apple")
        self.assertEqual(removed_item, self.apple)
        self.assertEqual(self.inv.inventory.get("apple", 0), 0)

    def test_get_recent_deltas(self):
        self.inv.add_item(self.apple)
        self.inv.add_item(self.orange)
        recent_deltas = self.inv.get_recent_deltas(2)
        self.assertEqual(recent_deltas, [("add", "apple", self.apple.id), ("add", "orange", self.orange.id)])

    def test_deltas_after_removal(self):
        self.inv.add_item(self.apple)
        self.inv.remove_item("apple")
        recent_deltas = self.inv.get_recent_deltas(2)
        self.assertEqual(recent_deltas, [("add", "apple", self.apple.id), ("remove", "apple", self.apple.id)])


if __name__ == "__main__":
    unittest.main()
