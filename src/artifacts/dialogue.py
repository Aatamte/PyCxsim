import dataclasses
from src.artifacts.artifact import Artifact
from copy import deepcopy


@dataclasses.dataclass
class Message:
    sender: int
    recipient: int
    content: int


class Dialogue(Artifact):
    def __init__(self):
        super().__init__("Dialogue")
        self.messages = {}

    def send_message(self, sender, recipient, content):
        if recipient in self.messages.keys():
            self.messages[recipient].append(Message(sender, recipient, content))
        else:
            self.messages[recipient] = [Message(sender, recipient, content)]

    def execute(self, agent, action):
        if isinstance(action, Message):
            self.send_message(action.sender, action.recipient, action.content)
        # Messages can be sent within the execute function based on agent logic
        self.send_message(agent.name, action[0], action[1])

    def generate_observations(self, agents):
        # The observations are the messages sent to each agent
        messages = self.messages.copy()
        self.messages.clear()
        return messages
