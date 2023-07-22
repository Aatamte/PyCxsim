import random
import numpy as np
import logging

from src.agents.base_agent import BaseAgent
from src.environment.artifacts.artifact import Artifact

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))


class BaseEnvironment:
    """
    BaseEnvironment is a class
    """

    def __init__(
            self,
            max_steps: int = 1000,
            verbose: int = 0,
            seed: int = None
    ):
        self.max_steps = max_steps
        self.verbose = verbose
        self.seed = seed
        self.artifact_handler = ArtifactHandler()

        self.current_step = None
        self.current_episode = 0

        # agent attributes
        self.agents = None
        self.n_agents = None
        self.agent_name_lookup = {}

        # logger
        console_handler.setLevel(logging.CRITICAL)
        logger.addHandler(console_handler)

    def populate(self, agents) -> None:
        if isinstance(agents, BaseAgent):
            agents = [agents]
        elif not isinstance(agents, list):
            raise TypeError(
                "Pass a list of BaseAgents. If only one agent, pass a list of length one"
            )

        self.agents = agents
        self.n_agents = len(agents)

        names = {}

        for idx, agent in enumerate(self.agents):
            agent.id = idx
            # set agent name or
            # change agent name if more than one agent with the same name
            if agent.name not in names.keys():
                names[agent.name] = 0
            else:
                names[agent.name] += 1
                agent.name = agent.name + "_" + str(names[agent.name])

        self.agent_name_lookup = {agent.name: agent for agent in self.agents}

    def add(self, artifact):
        self.artifact_handler.add_artifact(artifact)

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

        #time.sleep(0.01)
        return self.get_state(), {}

    def get_state(self) -> np.ndarray:
        return []

    def get_observation(self):
        raise NotImplementedError()

    def step(self, actions) -> [np.ndarray, list, list]:
        self.artifact_handler.step(actions)

        for agent in self.agents:
            agent.step()

        # CODE THAT HAPPENS AFTER ALL EVENTS ARE PROCESSED
        dones = [self.current_step >= self.max_steps for _ in self.agents]

        self.current_step += 1

        return self.get_state(), 0, dones

    def describe_actions(self):
        print("all actions take the form of a tuple, where the first element is a str of which artifact will handle action")

    def __repr__(self):
        newline = '\n'
        return \
f"""
                        Environment
Episode: {self.current_episode} / {self.max_steps}
Step: {self.current_step} / {self.max_steps}
                        Artifacts 
{str(self.artifact_handler)}
                        Agents
{newline.join([f"{idx}. "+ str(agent.name) for idx, agent in enumerate(self.agents)])}
"""


class ArtifactHandler:
    def __init__(self):
        self.artifacts: dict[str, Artifact] = {}

    def step(self, actions):
        for idx, action in enumerate(actions):
            agent = action[0]
            if not isinstance(agent, BaseAgent):
                raise TypeError("The first element in the action tuple must be of type <BaseAgent>")

            artifact_name = action[1]
            if artifact_name in self.artifacts.keys():
                self.artifacts[artifact_name].step(action[0], action[2])

    def add_artifact(self, artifact: Artifact):
        self.artifacts[artifact.name] = artifact

    def __repr__(self):

        return str(self.artifacts)

