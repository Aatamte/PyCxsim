import dataclasses
from collections import deque

from src.cxsim.artifacts.artifact import Artifact
from src.cxsim.prompts.prompt import Prompt


@dataclasses.dataclass
class Message:
    """Send a message to other agents in the simulation. Be clear and concise in your message. Do not be repetitive. Call out other agents who are repetitive, or who are sending to many messages.
    recipients: names of the other agent in the simulation, delimited by a comma. (example: 'John,Terry')
    content: text you want to send"""
    recipients: str
    content: str


@dataclasses.dataclass
class DialogueQuery:
    verbose: int


class Dialogue(Artifact):
    """Use this artifact to communicate with other agents in the environment"""
    def __init__(self):
        super().__init__("Dialogue")
        self.messages = {}
        self.action_space = [Message]
        #self.query_space = [DialogueQuery]

    def reset(self, environment):
        self.environment = environment
        for agent in self.environment.agents:
            self.messages[agent.name] = []

    def set_up(self, environment):
        self.environment = environment
        for agent in self.environment.agents:
            self.messages[agent.name] = deque()

    def process_action(self, agent, action: Message):
        print(agent, action)
        for recipient in action.recipients.split(","):
            recipient = recipient.strip()
            self.messages[recipient].append(action.content)
            self.environment.agent_name_lookup[recipient].inbox.append("From: " + agent.name + f"\nTo: {action.recipients}\nContent: " + action.content)

        return "Successful"


class Inbox:
    def __init__(self):
        pass