from src.agents.base_agent import BaseAgent


class Artifact:
    def __init__(self):
        self.interaction_map: dict
        self.name = "default"

    def say_hello(self):
        print("hello")

    def one_to_one_interaction(self, agent_from: BaseAgent, agent_to: BaseAgent):
        pass

    def step(self, agent, action):
        pass


