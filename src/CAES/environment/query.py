from dataclasses import dataclass


@dataclass
class Query:
    content: str = "default"

    def create_prompt(self):
        pass
