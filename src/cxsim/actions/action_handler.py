from src.cxsim.artifacts.artifact import Artifact


class ActionHandler:
    def __init__(self, environment):
        self.environment = environment
        self.artifacts: dict = {}

        self.action_logs = []
        self.query_logs = []

        self.map_action_to_artifact = {}
        self.map_query_to_artifact = {}

        self.action_lookup = {}

        self.agent_lookup = self.environment.agent_name_lookup

    def add_artifact(self, artifact: Artifact):
        self.artifacts[artifact.name] = artifact

        # add actions to map_action_to_artifact
        for action in artifact.get_action_space():
            self.map_action_to_artifact[action] = artifact.name

            self.action_lookup[action.__name__] = action

    def set_up(self):
        for artifact_name, artifact in self.artifacts.items():
            artifact.set_up()

    @staticmethod
    def is_restricted_action(agent, action):
        if type(action) not in agent.action_restrictions:
            return False
        else:
            for restriction in agent.action_restrictions[type(action)]:
                try:
                    restriction(agent, action)
                except AssertionError:
                    return True
        return False

    def process_action(self, agent, action):
        action_log = [self.environment.current_step, None, None]

        if action["action"] == "skip":
            action = None

        elif action["action"] in self.action_lookup.keys():
            action = self.action_lookup[action["action"]](*action["parameters"])
            action.agent = agent

        if action and not self.is_restricted_action(agent, action):
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
                self.artifacts[self.map_action_to_artifact[type(action)]].process_action(agent, action)
            else:
                raise Warning("An agents action must be either a tuple or an action class")
        agent.action_history.append(action)
        self.action_logs.append((agent.name, *action_log))

    def process_query(self, agent, query):
        artifact = self.map_query_to_artifact[type(query)]
        observation = self.artifacts[artifact].process_query(agent, query)
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


if __name__ == '__main__':
    pass