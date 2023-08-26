import time
import numpy as np
import logging
import h5py
import names
import random
import dearpygui.dearpygui as dpg
import multiprocessing


from src.CAES.agents.agent import Agent
from src.CAES.agents.population import Population
from src.CAES.artifacts.artifact import Artifact, ArtifactController
from src.CAES.visualization.visualizer import Visualizer
from src.CAES.environment.calander import Calender
from src.CAES.agents.items import ItemGenerator
from src.CAES.prompts.prompt import SystemPrompt, ObservationPrompt


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))


class UnsupportedItemType(Exception):
    """Exception raised when an unsupported item is added to the environment."""


def generate_random_adjacency_matrix(size):
    # Generate a random adjacency matrix with values from 0 to max_line_thickness
    adjacency_matrix = [[random.randint(0, 1) for _ in range(size)] for _ in range(size)]

    # Since adjacency matrix is symmetric, we copy the lower triangle to the upper triangle
    for i in range(size):
        for j in range(i+1, size):
            adjacency_matrix[i][j] = adjacency_matrix[j][i]

    return adjacency_matrix


class Environment:
    def __init__(
        self,
        name: str = "default environment",
        visualization: bool = False,
        save_to_file: bool = False,
        verbose: int = 0,
        seed: int = None,
        log: bool = False
    ):
        """
        Initialize the environment.

        :param name: Name of the environment
        :param record_environment: Whether to record the environment
        :param verbose: Verbosity level
        :param seed: Seed for random number generation
        :param filename: Name of the file to record the environment
        """
        self.name = name
        self.verbose = verbose
        self.seed = seed
        self.visualization = visualization

        self.should_stop_simulation = False
        self.is_first_step = True
        self.step_delay = 1

        self.current_step = 0
        self.max_steps = 100

        self.current_episode = 0
        self.max_episodes = 1

        # artifacts
        self.n_artifacts = 0
        self.artifact_controller = ArtifactController(self)
        self.calender = Calender()
        self.item_generator = ItemGenerator

        # agent attributes
        self.agents = []
        self.agent_names = []
        self.n_agents = 0
        self.agent_idx = 0
        self.agent_name_lookup = {}
        self.agent_id_lookup = {}

        self.action_space = {}
        self.query_space = {}

        # logger
        console_handler.setLevel(logging.CRITICAL)
        logger.addHandler(console_handler)

        self.save_to_file = save_to_file

        if self.save_to_file:
            pass
            #self.recorder = RecordedEnvironment("env_record.hdf5")

        if self.visualization:
            self.visualizer = Visualizer(self)

        self._current_time = time.perf_counter()
        self._past_time = time.perf_counter()

    def add_agent(self, agent: Agent):
        """
        Add a new agent to the environment.

        :param agent: An Agent object
        """
        agent.id = self.agent_idx
        self.agent_idx += 1
        agent.name = names.get_first_name()
        if self.agents:
            while agent.name in [a.name for a in self.agents]:
                agent.name = names.get_first_name()
        self.agent_names.append(agent.name)
        self.agents.append(agent)
        self.agent_name_lookup[agent.name] = agent
        self.n_agents = len(self.agents)

    def add_artifact(self, artifact: Artifact):
        """
        Add a new artifact to the environment.

        :param artifact: An Artifact object
        """
        self.artifact_controller.add_artifact(artifact)

    def add(self, item):
        """
        Add a new item (agent, artifact, or list) to the environment.

        :param item: Item to be added
        """
        if isinstance(item, Artifact):
            self.add_artifact(item)
        elif isinstance(item, Agent):
            self.add_agent(item)
        elif isinstance(item, Population):
            for it in item.generate_agents():
                self.add_agent(it)
        elif isinstance(item, list):
            for it in item:
                self.add(it)
        else:
            raise UnsupportedItemType()

    def validate_agents(self):
        for agent in self.agents:

            # make sure that all agents have an execute_action
            assert agent.execute_action.__code__ != Agent.execute_action.__code__, "execute_action method must be implemented by subclass"

            assert agent.execute_query.__code__ != Agent.execute_query.__code__, "execute_query method must be implemented by subclass"

    def validate_artifacts(self):
        for name, artifact in self.artifact_controller.artifacts.items():
            assert artifact.execute_action.__code__ != Artifact.execute_action.__code__, "execute_action method must be implemented by subclass"

            assert artifact.execute_query.__code__ != Artifact.execute_query.__code__, "execute_query method must be implemented by subclass"

    def set_up(self):
        # go through the artifacts and set them up

        system_prompt = SystemPrompt()

        for name, artifact in self.artifact_controller.artifacts.items():
            artifact.set_up()

            self.action_space[artifact.name] = artifact.get_action_space()

            self.query_space[artifact.name] = artifact.get_query_space()

            artifact.environment = self
            artifact.agents = self.agent_id_lookup

            system_prompt.insert_artifact_description(artifact.system_prompt.content)

            system_prompt.insert_global_action(artifact.get_action_space_prompt())

        for agent in self.agents:

            agent.action_space = self.action_space.copy()

            agent.query_space = self.query_space.copy()

            agent_system_prompt = system_prompt.copy()

            agent_system_prompt.set_starting_inventory(str(agent.starting_inventory))

            agent_system_prompt.set_action_restrictions(agent.action_restrictions)

            agent_system_prompt.set_environment_information(str(len(self.agents)), str(self.max_steps))

            agent_system_prompt.set_num_artifacts(str(len(self.artifact_controller.artifacts)))

            agent_system_prompt.set_artifact_descriptions()

            agent_system_prompt.set_global_actions()

            agent.system_prompt = agent_system_prompt

            agent.set_up()

        # assert that all agents have necessary functionality
        self.validate_agents()

        # assert that all artifacts have necessary functionality
        self.validate_artifacts()

        self.n_artifacts = len(self.artifact_controller.artifacts)
        # give agents the system prompt

        self.reset()

    def reset(self) -> [np.ndarray, dict]:
        """
        Resets the environment
        """
        if not self.agents:
            raise ValueError("agents must be passed through the <set_agents> function before  "
                             "the first episode is run")
        self.current_step = 0
        self.current_episode += 1

        # reset each agent
        for agent in self.agents:
            agent.reset()

        # reset artifacts
        self.artifact_controller.reset(self)

        if self.visualization:
            self.visualizer.reset(self)

        self.item_generator = ItemGenerator(self.agents)
        self.item_generator.generate_agent_items()
        return 0

    def update_simulation_state(self):
        self.current_step += 1
        if self.current_step >= self.max_steps:
            self.current_episode += 1
            self.current_step = 0
        if self.current_episode >= self.max_episodes:
            self.should_stop_simulation = True

        self.calender.step()

    def step(self) -> [np.ndarray, list, list]:
        if self.visualization:
            if self.visualizer.skip_steps > 0:
                self.visualizer.skip_steps -= 1
                self.visualizer.step(True)
            else:
                while (time.perf_counter() - self._current_time <= self.step_delay) or self.visualizer.is_paused:
                    self.visualizer.step(False)
                    if self.visualizer.skip_steps != 0:
                        self.visualizer.skip_steps -= 1
                        break
                else:
                    self.visualizer.step(True)

        self._current_time = time.perf_counter()

        # execute actions for each agent all actions are processed
        for agent in self.agents:

            # agent makes a query for information, receives an observation
            query = agent.execute_query()
            observation = self.artifact_controller.execute_query(agent, query)
            observation_prompt = ObservationPrompt()
            observation_prompt.set_current_step(str(self.current_step))
            observation_prompt.set_inventory(str(agent.display_inventory()))
            observation_prompt.insert_artifact_information(observation)
            observation_prompt.set_artifact_information()

            # append observation to the agents messages
            agent.messages.append({"role": "user", "content": observation_prompt.content})

            # agent chooses action based on the observation
            agent.execute_action()

        self.visualizer.running_background_tasks()

        for agent in self.agents:
            action = agent.action_queue.pop(0)
            print(action)
            # process logic for the action
            self.artifact_controller.process_action(agent, action)

            agent.step()

        self.artifact_controller.step()

        # should simulation stop based on response from artifacts
        should_continue = self.artifact_controller.should_continue()

        self.update_simulation_state()
        return should_continue

    def action_logs(self):
        return self.artifact_controller.action_logs

    def is_running(self):
        if self.visualization:
            if self.should_stop_simulation:
                del self.visualizer
                return False
            return dpg.is_dearpygui_running()
        else:
            return True

    def iter_steps(self):
        return range(0, self.max_steps)

    def iter_episodes(self):
        return range(0, self.max_episodes)

    def list_artifacts(self):
        return self.artifact_controller.artifacts

    def run(self, close_on_end: bool = True):
        #self.visualizer.start()
        for step in self.iter_steps():
            self.step()

    def save(self):
        print("saving")

    def load(self, filepath):
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

    def print_items(self):
        def print_attrs(name, obj):
            print(name)
            for key, val in obj.attrs.items():
                print("    %s: %s" % (key, val))
            if isinstance(obj, h5py.Dataset):  # check if the object is a dataset
                print("    value:", obj[()])

        with h5py.File("env_record.hdf5", "r") as f:
            f.visititems(print_attrs)




if __name__ == '__main__':
    # Initialize environment
    env = Environment(visualization=False)

    env.run()
