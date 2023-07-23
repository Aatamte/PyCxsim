import dataclasses
from src.environment.artifacts.artifact import Artifact


@dataclasses.dataclass
class Message:
    sender: int
    recipient: int
    content: int


class Dialogue(Artifact):
    def __init__(self):
        super().__init__("Dialogue")
        self.messages = []

    def send_message(self, sender, recipient, content):
        self.messages.append(Message(sender, recipient, content))

    def execute(self, agent, action_details):
        # Messages can be sent within the execute function based on agent logic
        pass

    def generate_observations(self):
        # The observations are the messages sent to each agent
        observations = {recipient: [] for _, recipient, _ in self.messages}
        for message in self.messages:
            observations[message.recipient].append(message.content)
        self.messages = []
        return observations
