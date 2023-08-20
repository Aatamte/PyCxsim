from dataclasses import dataclass
from CAES.src.agents.agent import Agent


@dataclass
class Query:
    content: str = "default"

    def create_prompt(self):
        pass
