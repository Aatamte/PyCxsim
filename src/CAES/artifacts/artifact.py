import json
from src.CAES.utilities.convert_string_to_json import string_to_dict


class Artifact:
    def __init__(self, name):
        self.name = name
        self.system_prompt = ""

        self.action_space_prompt = ""
        self.event_history = []

        self.environment = None
        self.agents = None

        self.action_space = []
        self.query_space = []

    def set_up(self):
        pass

    def execute_action(self, agent, action):
        pass

    def execute_query(self, agent, query):
        pass

    def step(self):
        pass

    def should_continue(self):
        return True

    def get_action_space(self):
        return self.action_space

    def get_action_space_prompt(self):
        return [action.create_prompt() for action in self.action_space]

    def get_query_space(self):
        return self.query_space

    def get_query_space_prompt(self):
        return [query.create_prompt() for query in self.query_space]

    def reset(self, environment):
        pass


class ArtifactActions:
    def __init__(self):
        pass


class ArtifactController:
    def __init__(self, environment):
        self.environment = environment
        self.artifacts: dict = {}

        self.action_logs = []
        self.query_logs = []

        self.map_action_to_artifact = {}
        self.map_query_to_artifact = {}

        self.action_lookup = {

        }

    def add_artifact(self, artifact: Artifact):
        self.artifacts[artifact.name] = artifact

        # add actions to map_action_to_artifact
        for action in artifact.get_action_space():
            self.map_action_to_artifact[action] = artifact.name

            self.action_lookup[action.__name__] = action

        # add queries to map_query_to_artifact
        for query in artifact.get_query_space():
            self.map_query_to_artifact[query] = artifact.name

    def set_up(self):
        for artifact_name, artifact in self.artifacts.items():
            artifact.set_up()

    def execute_action(self, agent, action):
        action_log = [self.environment.current_step, None, None]
        try:
            if action["action"] == "skip":
                action = None
            elif action["action"] in self.action_lookup.keys():
                action = self.action_lookup[action["action"]](**action["action_parameters"], agent=agent)
                print(action)

            if action is not None:
                if isinstance(action, tuple):
                    artifact_name, action_details = action
                    if artifact_name not in self.artifacts.keys():
                        raise KeyError(f"The artifact name that you supplied in the agents actions ({artifact_name}) does not exist in: {list(self.artifacts.keys())}")
                    artifact = self.artifacts[artifact_name]
                    action_log[1] = artifact_name
                    action_log[2] = action_details
                    artifact.execute_action(agent, action_details)
                elif type(action) in self.map_action_to_artifact.keys():
                    action_log[1] = self.map_action_to_artifact[type(action)]
                    action_log[2] = action
                    self.artifacts[self.map_action_to_artifact[type(action)]].execute_action(agent, action)
                else:
                    raise Warning("An agents action must be either a tuple or an action class")
            agent.action_history.append(action)
            self.action_logs.append((agent.name, *action_log))
        except Exception as e:
            print(e)
            print(action, agent)

    def execute_query(self, agent, query):
        artifact = self.map_query_to_artifact[type(query)]
        observation = self.artifacts[artifact].execute_query(agent, query)
        return observation

    def step(self):
        for name, artifact in self.artifacts.items():
            artifact.step()

    def should_continue(self):
        return all(artifact.should_continue() for artifact in self.artifacts.values())

    def reset(self, environment):
        for name, artifact in self.artifacts.items():
            artifact.reset(environment)

    def __repr__(self):
        return str(self.artifacts)


class AdjacencyMatrix:
    def __init__(self, agents):
        self.AdjacencyNameMatrix = [[]]

    def __getitem__(self, item):
        if isinstance(item, str):
            pass