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
        self.agent_idx = 0
        self.agent_name_lookup = {}
        self.agent_id_lookup = {}

        # logger
        console_handler.setLevel(logging.CRITICAL)
        logger.addHandler(console_handler)

    def add(self, item):
        if isinstance(item, Artifact):
            self.artifact_controller.add_artifact(item)
        elif isinstance(item, Agent):
            item.id = self.agent_idx
            self.agent_idx += 1
            self.agents.append(item)
            self.n_agents = len(self.agents)
        elif isinstance(item, list):
            for it in item:
                self.add(it)
        else:
            raise TypeError(
                "items should be either an Agent or Artifact"
            )

    def reset(self) -> [np.ndarray, dict]:
        """
        Resets the environment
        """
        if not self.agents:
            raise ValueError("agents must be passed through the <set_agents> function before the environment"
                             "the first episode is run")
        self.current_step = 0
        self.current_episode += 1

        # reset each agent
        for agent in self.agents:
            agent.reset()

        # reset artifacts
        self.artifact_controller.reset()

        return 0

    def step(self) -> [np.ndarray, list, list]:
        # after all actions are processed
        self.artifact_controller.execute(self.agents)

        # insert observations for the agents
        self.artifact_controller.insert_observations(self.agents)

        for agent in self.agents:
            agent.step()

        #
        should_continue = self.artifact_controller.should_continue()
        self.current_step += 1
        return should_continue

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


