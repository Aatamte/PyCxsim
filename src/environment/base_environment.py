import numpy as np
import logging
from src.agents.base_agent import Agent
from src.environment.artifacts.artifact import Artifact, ArtifactController
import h5py

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))


class Environment:
    def __init__(self, record_environment: bool = False, verbose: int = 0, seed: int = None):
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
        self.recorder = RecordedEnvironment("env_record.hdf5")

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

    def record_step(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.recorder.save_step(env=self)
            return result
        return wrapper

    @record_step
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

    def close(self):
        self.recorder.close()

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


def env_to_dict(env: Environment):
    return {
        "step": env.current_step,
        "max_steps": env.max_steps,
        "episode": env.current_episode,
        "max_episodes": env.max_episodes,
    }


class RecordedEnvironment:
    def __init__(self, filename):
        self.file = h5py.File(filename, 'w')

    def save_agent(self, agent):
        try:
            agent_group = self.file[str(agent.id)]
        except KeyError:
            agent_group = self.file.create_group(str(agent.id))
        print(agent.inventory.values())
        print(agent.observations)
        action_ds = agent_group.create_dataset(
            f'{agent.name}_{len(agent_group)}',
            data=np.array(list(agent.inventory.values())))
        action_ds.attrs['action'] = agent.action_queue
        #action_ds.attrs['inventory'] = agent.observations
        for idx, item in enumerate(agent.inventory.inventory.keys()):
            action_ds.attrs[f'item_{idx}'] = item

    def save_environment(self, env):
        try:
            env_group = self.file["environment"]
        except KeyError:
            env_group = self.file.create_group("environment")

        env_ds = env_group.create_group(f"env_{len(env_group)}")
        for key, value in env_to_dict(env).items():
            env_ds.create_dataset(key, data=value)

    def save_step(self, env: Environment):
        self.save_environment(env)

    def close(self):
        self.file.close()

