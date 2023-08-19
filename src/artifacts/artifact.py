from src.agents.agent import Agent


class Artifact:
    def __init__(self, name):
        self.name = name
        self.system_prompt = ""
        self.action_space_prompt = ""
        self.event_history = []

    def set_up(self):
        pass

    def execute(self, agent, action_details):
        pass

    def generate_observations(self, agents):
        return {agent.name: "Observation" for agent in agents}

    def display_actions(self):
        pass

    def step(self):
        pass

    def should_continue(self):
        return True

    @staticmethod
    def action_space():
        return []

    def process_summary(self):
        pass

    def execute_query(self):
        pass

    def reset(self, environment):
        pass

    def list_actions(self):
        pass

    def language_model_starting_prompt(self):
        pass


class ArtifactActions:
    def __init__(self):
        pass


class ArtifactController:
    def __init__(self):
        self.artifacts: dict[str, Artifact] = {}
        self.action_logs = []
        self.action_space_map = {}

    def add_artifact(self, artifact: Artifact):
        self.artifacts[artifact.name] = artifact

    def set_up(self):
        for artifact_name, artifact in self.artifacts.items():
            artifact.set_up()

    def execute_action(self, agent, action):
        self.action_logs.append((agent, action))
        agent.action_history.append(action)
        if action is not None:
            if isinstance(action, tuple):
                artifact_name, action_details = action
                if artifact_name not in self.artifacts.keys():
                    raise KeyError(f"The artifact name that you supplied in the agents actions ({artifact_name}) does not exist in: {list(self.artifacts.keys())}")
                artifact = self.artifacts[artifact_name]
                artifact.execute(agent, action_details)
            elif type(action) in self.action_space_map.keys():
                self.artifacts[self.action_space_map[type(action)]].execute(agent, action)
            else:
                raise Warning("An agents action must be either a tuple or an action class")

    def execute(self, agents):
        for idx, agent in enumerate(agents):
            if not isinstance(agent, Agent):
                raise TypeError("The first element in the action tuple must be of type <Agent>")
            if len(agent.action_queue) == 0:
                action = agent.select_action()
            else:
                action = agent.execute_next_action()

            self.execute_action(agent, action)
        return 0

    def step(self):
        for name, artifact in self.artifacts.items():
            artifact.step()

    def insert_observations(self, env, agents):
        artifact_observations = ""
        for artifact in self.artifacts.values():
            artifact_observations += artifact.generate_observations(agents)

        standard_environment_information = f"current step: {env.current_step}"

        full_observation = standard_environment_information + "\n" + artifact_observations

        for agent in agents:
            agent.get_observation(full_observation)

    def should_continue(self):
        return all(artifact.should_continue() for artifact in self.artifacts.values())

    def reset(self, environment):

        for name, artifact in self.artifacts.items():
            artifact.reset(environment)
            for action in artifact.action_space():
                self.action_space_map[action] = name

        print(self.action_space_map)

    def __repr__(self):
        return str(self.artifacts)


class AdjacencyMatrix:
    def __init__(self, agents):
        self.AdjacencyNameMatrix = [[]]

    def __getitem__(self, item):
        if isinstance(item, str):
            pass