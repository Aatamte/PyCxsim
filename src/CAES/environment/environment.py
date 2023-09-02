import time
import logging

import numpy as np
import names
import dearpygui.dearpygui as dpg

from src.CAES.agents.agent import Agent
from src.CAES.agents.population import Population
from src.CAES.artifacts.artifact import Artifact
from src.CAES.actions.action_handler import ActionHandler
from src.CAES.queries.query_handler import QueryHandler
from src.CAES.visualization.visualizer import Visualizer
from src.CAES.environment.calander import Calender
from src.CAES.agents.item import ItemHandler
from src.CAES.prompts.prompt import SystemPrompt, ObservationPrompt


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))


class UnsupportedItemType(Exception):
    """Exception raised when an unsupported item is added to the environment."""


class Environment:
    """
    Represents the simulation environment, managing agents, artifacts, actions, and the overall state.

    Attributes:
        name (str): Name of the environment.
        verbose (int): Verbosity level.
        seed (int): Seed for random number generation.
        visualization (bool): Whether to visualize the environment.
        start_time (float): Start time of the simulation.
        ... [other attributes]
    """
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

        :param name: Name of the environment.
        :param visualization: Whether to visualize the environment.
        :param verbose: Verbosity level.
        :param seed: Seed for random number generation.
        ... [other parameters]
        """
        self.name = name
        self.verbose = verbose
        self.seed = seed
        self.visualization = visualization
        self.start_time = None

        self.should_stop_simulation = False
        self.is_first_step = True
        self.step_delay = 1

        self.current_step = 0
        self.max_steps = 100

        self.current_episode = 0
        self.max_episodes = 1

        # agent attributes
        self.agents = []
        self.agent_names = []
        self.n_agents = 0
        self.agent_idx = 0
        self.agent_name_lookup = {}
        self.agent_id_lookup = {}

        self.action_space = {}
        self.query_space = {}

        # artifacts
        self.n_artifacts = 0
        self.artifacts = []

        self.action_handler = ActionHandler(self)
        self.query_handler = QueryHandler(self)

        self.calender = Calender()
        self.item_handler = ItemHandler(self)

        if self.visualization:
            self.visualizer = Visualizer(self)

        self._current_time = time.perf_counter()
        self._past_time = time.perf_counter()

        # logger
        console_handler.setLevel(logging.CRITICAL)
        logger.addHandler(console_handler)

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
        self.action_handler.add_artifact(artifact)
        self.query_handler.add_artifact(artifact)

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
        for name, artifact in self.action_handler.artifacts.items():
            assert artifact.set_up.__code__ != Artifact.process_query.__code__, "process_query method must be implemented by subclass"

            assert artifact.reset.__code__ != Artifact.reset.__code__, "process_query method must be implemented by subclass"

            assert artifact.process_action.__code__ != Artifact.process_action.__code__, "process_action method must be implemented by subclass"

            assert artifact.process_query.__code__ != Artifact.process_query.__code__, "process_query method must be implemented by subclass"

            assert len(artifact.action_space) != 0, "Action space must be greater than 0"

            assert len(artifact.query_space) != 0, "Query space must be greater than 0"

    def _set_up_artifacts(self):
        pass

    def set_up(self):
        self.start_time = time.perf_counter()
        # assert that all agents have necessary functionality
        self.validate_agents()

        # assert that all artifacts have necessary functionality
        self.validate_artifacts()

        system_prompt = SystemPrompt()
        # go through the artifacts and set them up
        for name, artifact in self.action_handler.artifacts.items():
            artifact.set_up(self)

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

            agent_system_prompt.set_starting_inventory(str(agent.inventory.starting_inventory))

            agent_system_prompt.set_action_restrictions(agent.action_restrictions)

            agent_system_prompt.set_environment_information(str(len(self.agents)), str(self.max_steps))

            agent_system_prompt.set_num_artifacts(str(len(self.action_handler.artifacts)))

            agent_system_prompt.set_artifact_descriptions()

            agent_system_prompt.set_global_actions()

            agent.system_prompt = agent_system_prompt

            agent.set_up()

        self.n_artifacts = len(self.action_handler.artifacts)
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
        self.action_handler.reset(self)

        if self.visualization:
            self.visualizer.reset(self)

        return 0

    def update_simulation_state(self):
        self.current_step += 1
        if self.current_step >= self.max_steps:
            self.current_episode += 1
            self.current_step = 0
        if self.current_episode >= self.max_episodes:
            self.should_stop_simulation = True

        self.calender.step()

    def process_agent_turn(self, agent):
        # agent makes a query for information
        query = agent.execute_query()

        observation = self.query_handler.process_query(agent, query)

        observation_prompt = ObservationPrompt()
        observation_prompt.set_current_step(str(self.current_step))
        observation_prompt.set_inventory(str(agent.display_inventory()))
        observation_prompt.insert_artifact_information(observation)
        observation_prompt.set_artifact_information()

        # append observation to the agents messages
        agent.messages.append({"role": "user", "content": observation_prompt.content})

        # agent chooses action based on the observation
        agent.execute_action()

        # wait until background tasks are complete
        self.visualizer.running_background_tasks()

        action = agent.action_queue.pop(0)

        # process logic for the action
        self.action_handler.process_action(agent, action)

        agent.step()

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
        num_tokens = []
        for agent in self.agents:
            self.process_agent_turn(agent)
            tokens = agent.usage_statistics["total_tokens"]
            print(tokens)
            num_tokens.append(agent.usage_statistics["total_tokens"])
        print(sum(num_tokens))
        print(sum(num_tokens) / (time.perf_counter() - self.start_time) * 60)
        self.action_handler.step()

        # should simulation stop based on response from artifacts
        should_continue = self.action_handler.should_continue()

        self.update_simulation_state()
        return should_continue

    def action_logs(self):
        return self.action_handler.action_logs

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
        return self.action_handler.artifacts

    def run(self, close_on_end: bool = True):
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
{str(self.action_handler)}
                        Agents
{newline.join([f"{idx}. "+ str(agent.name) for idx, agent in enumerate(self.agents)])}
"""
