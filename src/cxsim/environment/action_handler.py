from cxsim.artifacts.artifact import Artifact
from typing import Union, Tuple, Any, Type, List
from dataclasses import is_dataclass, asdict


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
        for action in artifact.action_space:
            self.map_action_to_artifact[action] = artifact.name
            self.action_lookup[action.__name__] = action

    def set_up(self):
        for artifact_name, artifact in self.artifacts.items():
            artifact.set_up()

    @staticmethod
    def is_restricted_action(agent, action: Any) -> Tuple[bool, Any]:
        action_type = type(action) if not is_dataclass(action) else action
        if action_type not in agent.action_restrictions:
            return False, None

        for restriction in agent.action_restrictions[action_type]:
            try:
                restriction(agent, action)
            except AssertionError as e:
                return True, e
        return False, None

    def process_action(self, agent, action: Any) -> str:
        if not is_dataclass(action):
            return "Invalid input: Action must be a dataclass."

        action_type = type(action)
        action_log = [self.environment.current_step, None, asdict(action)]

        if action_type not in self.map_action_to_artifact:
            return f"Invalid action: {action_type.__name__} is not in the list of available actions."

        artifact_name = self.map_action_to_artifact[action_type]
        artifact = self.artifacts.get(artifact_name, None)

        if artifact is None:
            return f"Invalid artifact: No artifact associated with action {action_type.__name__}."

        try:
            result = artifact.process_action(agent, action)
        except Exception as e:
            return f"Action processing failed: {e}"

        action_log[1] = artifact_name
        agent.action_history.append((self.environment.current_step, artifact_name, asdict(action)))
        self.action_logs.append((agent.name, *action_log))

        return f"Action processed successfully: {result}" if result else "Action processed successfully."

    def step(self):
        for name, artifact in self.artifacts.items():
            artifact.step()

    def should_continue(self):
        return all(artifact.should_continue() for artifact in self.artifacts.values())

    def __repr__(self):
        return str(self.artifacts)


if __name__ == '__main__':
    pass