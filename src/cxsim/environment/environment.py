import time
import logging
import numpy as np
import names
import dearpygui.dearpygui as dpg
from collections import deque
from functools import wraps
from dataclasses import is_dataclass, asdict
from typing import Union, Any

# core
from src.cxsim.agents.agent import Agent
from src.cxsim.agents.population import Population
from src.cxsim.artifacts.artifact import Artifact
from src.cxsim.actions.action_handler import ActionHandler
from src.cxsim.gui.visualizer import GUI
from src.cxsim.utilities.background_jobs.background_task import BackgroundTask
from src.cxsim.environment.utilities import EnvironmentUtilities

# misc
from src.cxsim.environment.calander import Calender
from src.cxsim.agents.item import ItemHandler
from src.cxsim.environment.event import Event, EventHandler

# actions
from src.cxsim.actions.standard import STANDARD_ACTIONS


class UnsupportedItemType(Exception):
    """Exception raised when an unsupported item is added to the environment."""


class Environment:
    """
    Represents the simulation environment, managing agents, artifacts, actions, and the overall state.

    Attributes:
        name (str): Name of the environment.
        verbose (int): Verbosity level.
        seed (int): Seed for random number generation.
        gui (bool): Whether to visualize the environment.
        _start_time (float): Start time of the simulation.
        ... [other attributes]
    """
    def __init__(
            self,
            name: str = "default environment",
            max_steps: int = 10,
            max_episodes: int = 10,
            step_delay: int = 2,
            gui: GUI = GUI(),
            verbose: int = 0,
            reuse_names: bool = True,
            seed: int = None,
    ):
        """
        Initialize the environment.

        :param name: Name of the environment.
        :param gui: Whether to visualize the environment.
        :param verbose: Verbosity level.
        :param seed: Seed for random number generation.
        ... [other parameters]
        """
        self.name = name
        self.verbose = verbose
        self.seed = seed
        self.gui = gui
        self._start_time = None

        # gridworld
        self.starting_block_size = 15

        # logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self._should_stop_simulation = False
        self._is_first_step = True
        self._is_prepared = False
        self.step_delay = step_delay

        self.current_step = 0
        self.max_steps = max_steps

        self.current_episode = 0
        self.max_episodes = max_episodes

        # agent attributes
        self.agents = []
        self.agent_names = []
        self.n_agents = 0
        self.agent_idx = 0
        self.agent_name_lookup = {}
        self.agent_id_lookup = {}

        # actions
        self.max_actions = 1
        self.action_space = {}
        self.standard_actions = STANDARD_ACTIONS

        # artifacts
        self.n_artifacts = 0
        self.artifacts = []
        self.artifact_lookup = {}

        # handlers
        self.action_handler = ActionHandler(self)
        self.event_handler = EventHandler(self)

        # utilities
        self.utils: EnvironmentUtilities = EnvironmentUtilities()

        # agent queue
        self.agent_queue = deque()

        self.calender = Calender()
        self.item_handler = ItemHandler(self)

        self.gui = gui

        if self.gui:
            self.gui.prepare(self)

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
        self.action_handler.add_artifact(artifact)
        self.artifacts.append(artifact)
        self.artifact_lookup[artifact.name] = artifact

    def add_event(self, event: Event):
        self.event_handler.add_event(event)

    def add(self, item):
        """
        Add a new item (agent, artifact, population, event, or a list of valid items) to the environment.

        :param item: Item to be added
        """
        if isinstance(item, Artifact):
            self.add_artifact(item)
        elif isinstance(item, Agent):
            self.add_agent(item)
        elif isinstance(item, Population):
            for it in item:
                self.add_agent(it)
        elif isinstance(item, Event):
            self.add_event(item)

        elif isinstance(item, list):
            for it in item:
                self.add(it)
        else:
            raise UnsupportedItemType()

    def validate_agents(self):
        for agent in self.agents:
            pass

    def validate_artifacts(self):
        for name, artifact in self.action_handler.artifacts.items():
            assert artifact.reset.__code__ != Artifact.reset.__code__, "process_query method must be implemented by subclass"
            assert artifact.process_action.__code__ != Artifact.process_action.__code__, "process_action method must be implemented by subclass"

    def compile(self):
        self._start_time = time.perf_counter()
        # assert that all agents have necessary functionality
        self.validate_agents()

        # assert that all artifacts have necessary functionality
        self.validate_artifacts()

        # go through the artifacts and set them up
        for name, artifact in self.action_handler.artifacts.items():
            artifact.set_up(self)

            self.action_space[artifact.name] = artifact.get_action_space()

            artifact.agents = self.agent_id_lookup

            for agent in self.agents:
                agent.action_space = self.action_space.copy()
                agent.step = wrap_with_background_task(agent.step, agent, self.gui)
                agent.environment = self
                agent.compile()

        self.n_artifacts = len(self.action_handler.artifacts)
        self._is_prepared = True

    def reset(self) -> [np.ndarray, dict]:
        """
        Resets the environment
        """

        if not self.agents:
            raise ValueError("agents must be passed through the <set_agents> function before  "
                             "the first episode is run")

        if not self._is_prepared:
            self.compile()

        self.current_step = 0
        self.current_episode += 1

        # reset each agent
        for agent in self.agents:
            agent.reset()

        # add agent to the agent queue
        for agent in self.agents:
            self.agent_queue.append(agent)

        # reset artifacts
        self.action_handler.reset(self)

        if self.gui:
            self.gui.reset(self)
            self.gui.run_event_loop(self._current_time)

        return 0

    def update_simulation_state(self):
        self.current_step += 1
        if self.current_step >= self.max_steps:
            self.current_episode += 1
            self.current_step = 0
        if self.current_episode >= self.max_episodes:
            self._should_stop_simulation = True

        self.calender.step()

    def process_action(self, agent, action: Union[dict, Any]) -> Any:
        # Generate a mapping of action names from the agent's action space
        action_names = {(item.__name__.lower()): item for value in agent.action_space.values() for item in value}

        # Initialize the observation to None
        observation = None

        # If action is a dataclass, convert it to dictionary
        if is_dataclass(action):
            action = asdict(action)

        # Extract the action name and parameters
        action_name, action_params = list(action.items())[0]
        action_name = action_name.lower()
        print(action_name, action_names)

        # Check if the action exists in the action space
        if action_name in action_names:
            ActionClass = action_names[action_name]  # Get the corresponding class
            # Convert the action_params dict to a dataclass instance if it isn't already
            if not is_dataclass(action_params):
                action_params = ActionClass(**action_params)
            # Process the action and get an observation
            observation = self.action_handler.process_action(agent, action_params)

        return observation

    def process_turn(self, agent: Agent):
        # Before turn methods
        for func in agent.before_turn_methods:
            func()

        agent.step()


        # After turn methods
        for func in agent.after_turn_methods:
            func()

    def step(self) -> [np.ndarray, list, list]:
        if self.gui:
            self.gui.run_event_loop(self._current_time)

        self._current_time = time.perf_counter()

        if len(self.agent_queue) != 0:
            for _ in range(len(self.agent_queue)):
                agent = self.agent_queue.popleft()
                self.process_turn(agent)

        assert len(self.agent_queue) == 0, "Unexpected behavior: Agent queue should be empty"

        for agent in self.agents:
            self.agent_queue.append(agent)

        self.action_handler.step()

        # should simulation stop based on response from artifacts
        should_continue = self.action_handler.should_continue()

        self.update_simulation_state()

    def describe(self):
        pass

    def action_logs(self):
        return self.action_handler.action_logs

    def is_running(self):
        if self.gui:
            if self._should_stop_simulation:
                del self.gui
                return False
            return dpg.is_dearpygui_running()
        else:
            return True

    def iter_steps(self):
        return range(0, self.max_steps)

    def iter_episodes(self):
        return range(0, self.max_episodes)

    def iter_agent_turns(self):
        while len(self.agent_queue) > 0:
            yield self.agent_queue.popleft()

    def list_artifacts(self):
        return self.action_handler.artifacts

    def run(self, close_on_end: bool = True):
        for step in self.iter_steps():
            self.step()

    def __getitem__(self, item):
        if item in self.artifact_lookup.keys():
            return self.artifact_lookup[item]
        else:
            raise KeyError("Artifact not in environment")

    def save(self):
        print("saving")

    def load(self, filepath):
        pass

    @property
    def agent_queue_length(self):
        return len(self.agent_queue)

    def log(self, level, msg, *args, **kwargs):
        """
        Convenience method for logging messages.

        :param level: The logging level.
        :param msg: The format string for the message.
        :param args: The arguments to merge into msg.
        :param kwargs: Other keyword arguments.
        """
        self.logger.log(level, msg, *args, **kwargs)

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


def wrap_with_background_task(original_func, agent, gui):
    @wraps(original_func)
    def wrapper(*args, **kwargs):
        with BackgroundTask(original_func, gui, agent_name=agent.name):
            pass
    return wrapper
