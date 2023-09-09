from src.cxsim.agents.tools.tool import Tool
from src.cxsim.prompts.prompt import Prompt


class KnowledgeBase(Tool):
    def __init__(self):
        super().__init__(name="KnowledgeBase",
                         description="A foundational tool designed to store, retrieve, modify, and manage facts.")
        self.data = {}
        self.full_description_prompt = Prompt(content="")

    def add_entry(self, key: str, value: str):
        """Add an entry to the knowledge base."""
        self.data[key] = value

    def get_entry(self, key: str) -> str:
        """Retrieve an entry from the knowledge base."""
        return self.data.get(key, "Entry not found.")

    def update_entry(self, key: str, value: str):
        """Update an existing entry in the knowledge base."""
        if key in self.data:
            self.data[key] = value
        else:
            raise KeyError(f"No entry found for key '{key}'.")

    def delete_entry(self, key: str):
        """Delete an entry from the knowledge base."""
        if key in self.data:
            del self.data[key]
        else:
            raise KeyError(f"No entry found for key '{key}'.")

    def list_entries(self) -> list:
        """List all keys in the knowledge base."""
        return list(self.data.keys())


# Example usage:
if __name__ == '__main__':
    # 1. Create an instance of the KnowledgeBase class.
    kb = KnowledgeBase()

    # 2. Add some entries.
    kb.add_entry("Eiffel Tower", "A wrought-iron lattice tower in Paris, France.")
    kb.add_entry("Great Wall of China",
                 "A series of fortifications made of stone, brick, and other materials, built along the northern borders of China.")

    # 3. Retrieve an entry.
    print(kb.get_entry("Eiffel Tower"))  # Output: A wrought-iron lattice tower in Paris, France.

    # 4. Update an entry.
    kb.update_entry("Eiffel Tower", "A famous landmark in Paris, France, made of iron.")

    # 5. List all entries.
    print(kb.list_entries())  # Output: ['Eiffel Tower', 'Great Wall of China']

    # 6. Delete an entry.
    kb.delete_entry("Great Wall of China")

    # 7. Try retrieving the deleted entry.
    print(kb.get_entry("Great Wall of China"))  # Output: Entry not found.
