class Tool:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def get_name(self) -> str:
        """Return the name of the tool."""
        return self.name

    def get_description(self) -> str:
        """Return the description of the tool."""
        return self.description

    def display_info(self):
        """Display the tool's name and description."""
        print(f"Tool Name: {self.name}")
        print(f"Description: {self.description}")