from src.cxsim.artifacts.artifact import Artifact
from src.cxsim.prompts.prompt import ObservationPrompt


class QueryHandler:
    def __init__(self, environment):
        self.environment = environment
        self.artifacts: dict = {}

        self.query_logs = []

        self.map_query_to_artifact = {}
        self.action_list = []

        self.query_lookup = {}

    def add_artifact(self, artifact: Artifact):
        self.artifacts[artifact.name] = artifact

        # add queries to map_query_to_artifact
        for query in artifact.get_query_space():
            self.map_query_to_artifact[query] = artifact.name
            self.query_lookup[query.__name__] = query

        for action in artifact.get_action_space():
            self.action_list.append(action.__name__)

    @staticmethod
    def is_restricted_query(agent, action):
        if type(action) not in agent.action_restrictions:
            return False
        else:
            for restriction in agent.action_restrictions[type(action)]:
                try:
                    restriction(agent, action)
                except AssertionError:
                    return True
        return False

    def process_query(self, agent, query):
        name = query["query"]
        if name == "Skip":
            return False, None, False
        else:
            query = self.query_lookup[name](*query["parameters"])
        print(query)
        artifact = self.map_query_to_artifact[type(query)]
        observation = self.artifacts[artifact].process_query(agent, query)
        return True, observation, False


if __name__ == '__main__':
    pass