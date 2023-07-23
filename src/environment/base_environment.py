import numpy as np
import logging
from src.agents.base_agent import Agent
from src.environment.artifacts.artifact import Artifact, ArtifactController

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
        # after all actions are processed
        self.artifact_controller.execute(self.agents)

        # insert observations for the agents
        self.artifact_controller.insert_observations(self.agents)

        for agent in self.agents:
            agent.step()

        # CODE THAT HAPPENS AFTER ALL EVENTS ARE PROCESSED
        dones = [self.current_step >= self.max_steps for _ in self.agents]
        self.current_step += 1
        return 0

    def run(self):
        for episode in range(self.max_episodes):
            self.reset()
            for step in range(self.max_steps):
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


