import dataclasses
from collections import deque

from src.cxsim.artifacts.artifact import Artifact
from src.cxsim.prompts.prompt import Prompt


@dataclasses.dataclass
class Message:
    recipient: int
    content: int


@dataclasses.dataclass
class DialogueQuery:
    verbose: int


class Dialogue(Artifact):
    def __init__(self):
        super().__init__("Dialogue")
        self.messages = {}
        self.action_space = [
            Message
        ]
        self.query_space = [
            DialogueQuery
        ]

    def reset(self, environment):
        self.environment = environment
        self.messages = {}

    def set_up(self, environment):
        self.environment = environment
        for agent in self.environment.agents:
            self.messages[agent.name] = deque()

        self.system_prompt = Prompt(
            f"""This is a marketplace where agents can buy and sell goods. A positive quantity represents a buy order, while a negative quantity represents a sell order. If there are no other orders in the marketplace, you are required to submit an order (you may choose parameters that are unrealistic, but valid)"""
        )

    def process_action(self, agent, action: Message):
        self.messages[action.recipient].push(action.content)

    def process_query(self, agent, query):
        return self.messages[agent.name]


class Inbox:
    def __init__(self):
        pass