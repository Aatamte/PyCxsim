from src.agents.base_agent import Agent


class Artifact:
    def __init__(self, name):
        self.name = name

    def execute(self, agent, action_details):
        pass

    def generate_observations(self, agents):
        return {agent.name: "Observation" for agent in agents}

    def describe_actions(self):
        pass

    def should_continue(self):
        return True

    def reset(self):
        pass


class ArtifactController:
    def __init__(self):
        self.artifacts: dict[str, Artifact] = {}

    def add_artifact(self, artifact: Artifact):
        self.artifacts[artifact.name] = artifact

    def execute_action(self, agent, action):
        artifact_name, action_details = action
        if artifact_name not in self.artifacts.keys():
            raise KeyError(f"The artifact name that you supplied ({artifact_name}) does not exist in: {list(self.artifacts.keys())}")
        artifact = self.artifacts[artifact_name]
        artifact.execute(agent, action_details)

    def execute(self, agents):
        for idx, agent in enumerate(agents):
            if not isinstance(agent, Agent):
                raise TypeError("The first element in the action tuple must be of type <BaseAgent>")

            if len(agent.action_queue) == 0:
                agent.select_action()
            action = agent.execute_next_action()
            self.execute_action(agent, action)
        return 0

    def insert_observations(self, agents):
        agent_observations_per_artifact = {agent.name: {} for agent in agents}

        for artifact_name, artifact in self.artifacts.items():
            all_agent_observations = artifact.generate_observations(agents)
            for agent in agents:
                if agent.name not in all_agent_observations.keys():
                    continue
                agent_observations_per_artifact[agent.name][artifact_name] = all_agent_observations[agent.name]

        for agent in agents:
            agent.update(agent_observations_per_artifact[agent.name])

    def should_continue(self):
        return all(artifact.should_continue() for artifact in self.artifacts.values())

    def reset(self):
        for artifact in self.artifacts.values():
            artifact.reset()

    def __repr__(self):
        return str(self.artifacts)

