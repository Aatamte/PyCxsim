import numpy as np
import logging

from src.agents.base_agent import Agent
from src.environment.artifacts.artifact import Artifact

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))


class Environment:
    def __init__(self, verbose: int = 0, seed: int = None):
        self.verbose = verbose
        self.seed = seed

        self.current_step = 0
        self.max_steps = np.inf

        self.current_episode = 0
        self.max_episodes = np.inf

        # artifacts
        self.artifact_controller = ArtifactController()

        # agent attributes
        self.agents = []
        self.n_agents = 0
        self.agent_name_lookup = {}
        self.agent_id_lookup = {}

        # logger
        console_handler.setLevel(logging.CRITICAL)
        logger.addHandler(console_handler)

    def add(self, item):
        if isinstance(item, Artifact):
            self.artifact_controller.add_artifact(item)
        elif isinstance(item, Agent):
            self.agents.append(item)
            self.n_agents = len(self.agents)
        else:
            self.agents.extend(item)
            self.n_agents = len(self.agents)

    def reset(self) -> [np.ndarray, dict]:
        """
        Resets the environment - including agents and gridworld
        """
        if not self.agents:
            raise ValueError("agents must be passed through the <set_agents> function before the environment"
                             "the first episode is run")
        self.current_step = 0
        self.current_episode += 1

        # reset each agent
        for agent in self.agents:
            agent.reset()

        return 0

    def step(self) -> [np.ndarray, list, list]:
        # after all actions are processed, generate observations for the agents
        observations = self.artifact_controller.step(self.agents)

        for artifact_name, artifact_observations in observations.items():
            for agent in self.agents:
                if agent.name in artifact_observations:
                    pass

        for agent in self.agents:
            agent.step()
        # CODE THAT HAPPENS AFTER ALL EVENTS ARE PROCESSED
        dones = [self.current_step >= self.max_steps for _ in self.agents]
        self.current_step += 1
        return 0

    def run(self):
        for episode in range(10):
            self.reset()
            for step in range(10):
                pass

    def __repr__(self):
        newline = '\n'
        return \
f"""
                        Environment
Episode: {self.current_episode} / {self.max_steps}
Step: {self.current_step} / {self.max_steps}
                        Artifacts 
{str(self.artifact_controller)}
                        Agents
{newline.join([f"{idx}. "+ str(agent.name) for idx, agent in enumerate(self.agents)])}
"""


class ArtifactController:
    def __init__(self):
        self.artifacts: dict[str, Artifact] = {}

    def add_artifact(self, artifact: Artifact):
        self.artifacts[artifact.name] = artifact

    def handle_action(self, agent, action):
        artifact_name, action_details = action
        artifact = self.artifacts[artifact_name]
        artifact.execute(agent, action_details)

    def step(self, agents):
        for idx, agent in enumerate(agents):
            action = agent.execute_next_action()
            if not isinstance(agent, Agent):
                raise TypeError("The first element in the action tuple must be of type <BaseAgent>")
            self.handle_action(agent, action)

        return self.generate_observations()

    def generate_observations(self):
        observations = {}
        for artifact_name, artifact in self.artifacts.items():
            observations[artifact_name] = artifact.generate_observations()

        return observations

    def __repr__(self):
        return str(self.artifacts)

