import dataclasses
from collections import deque

from cxsim.artifacts.artifact import Artifact


@dataclasses.dataclass
class Message:
    """Send a message to other agents in the simulation. Be clear and concise in your message. Do not be repetitive. Call out other agents who are repetitive, or who are sending to many messages.
    recipients: names of the other agent in the simulation, delimited by a comma. (example: 'John,Terry')
    content: text you want to send"""
    recipients: str
    content: str


class Dialogue(Artifact):
    """Use this artifact to communicate with other agents in the environment"""
    def __init__(self):
        super().__init__("Dialogue")
        self.messages = {}
        self.action_space.append(Message)

    def reset(self, environment):
        self.environment = environment
        for agent in self.environment.agents:
            self.messages[agent.name] = []

    def step(self):
        pass

    def compile(self, environment):
        self.environment = environment
        for agent in self.environment.agents:
            self.messages[agent.name] = deque()

    def process_action(self, agent, action: Message):
        for recipient in action.recipients.split(","):
            recipient = recipient.strip()
            self.messages[recipient].append(action.content)
            self.environment.agent_name_lookup[recipient].inbox.append("From: " + agent.name + f"\nTo: {action.recipients}\nContent: " + action.content)

        return "Successful"
