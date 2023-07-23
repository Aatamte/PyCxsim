from src.agents.base_agent import Agent


class Artifact:
    def __init__(self, name):
        self.name = name
        self.interaction_map: dict

    def execute(self, agent, action_details):
        pass

    def generate_observations(self):
        pass


