import datetime
import time
import logging
from collections import deque
from functools import wraps
from dataclasses import is_dataclass, asdict
from typing import Union, Any, Dict
import inspect
from dataclasses import fields
import random

# core
from cxsim.agents.agent import Agent
from cxsim.agents.population import Population
from cxsim.artifacts.artifact import Artifact
from cxsim.environment.action_handler import ActionHandler
from cxsim.utilities.background_jobs.background_task import BackgroundTask
from cxsim.environment.utilities import EnvironmentUtilities
from cxsim.artifacts.standard.gridworld import Gridworld

# misc
from cxsim.agents.item import ItemHandler
from cxsim.environment.event import Event, EventHandler
from cxsim.utilities.names import get_first_name

# actions
from cxsim.agents.actions.standard import STANDARD_ACTIONS
from cxsim.agents.actions.action import Action

# GUI
from cxsim.environment.cx_socketio import CxSocket

# database
from cxsim.environment.database.cx_database import CxDatabase
from cxsim.environment.database.cx_table import CxTable
from cxsim.environment.database.default_tables import CxMetadata, CxAgents, CxLogs


class UnsupportedItemType(Exception):
    """Exception raised when an unsupported item is added to the environment."""


ENV_STATUS = {
    0: "Stopped",
    1: "Running",
    2: "Running next step"
}


class Environment:
    """
    Represents the simulation environment, managing agents, artifacts, actions, and the overall state.

    Attributes:
        name (str): Name of the environment.
        verbose (int): Verbosity level.
        seed (int): Seed for random number generation.
        ... [other attributes]
    """
    def __init__(
            self,
            name: str = "default environment",
            max_steps: int = 10,
            max_episodes: int = 10,
            step_delay: int = 2,
            verbose: int = 0,
            seed: int = None,
            use_gui: bool = True,
            use_database: Union[bool, CxDatabase] = True,
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

        self.use_gui = use_gui
        self.use_database = use_database

        self._start_time = None

        # logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self._should_stop_simulation = False

        self._is_first_step = True
        self._is_compiled = False

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
        self.agent_dict: Dict[str, Agent] = {}

        # actions
        self.action_space = {}
        self.standard_actions = STANDARD_ACTIONS

        # artifacts
        self.n_artifacts = 0
        self.artifacts = []
        self.artifact_names = []
        self.artifact_lookup = {}

        # required artifacts
        self.gridworld: Gridworld = None

        # handlers
        self.action_handler = ActionHandler(self)
        self.event_handler = EventHandler(self)

        # utilities
        self.utils: EnvironmentUtilities = EnvironmentUtilities(self)

        # agent queue
        self.agent_queue = deque()
        
        self.item_handler = ItemHandler(self)

        self._current_time = time.perf_counter()
        self._past_time = time.perf_counter()

        # mode
        self.strict = False

        # other variables
        self.STATUS = 0

        self.database: CxDatabase = None

        if self.use_database:
            self.database = CxDatabase()
            self.database.connect()
            self.database.reset()

        if self.use_gui:
            self.cx_socket = CxSocket(self, db=self.database)
            self.cx_socket.run()

    def add_agent(self, agent: Agent):
        """
        Add a new agent to the environment.

        :param agent: An Agent object
        """
        agent.id = self.agent_idx
        self.agent_idx += 1
        agent.name = get_first_name()
        while agent.name in self.agent_names or agent.name == "" or len(agent.name) >= 5:
            agent.name = get_first_name()
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
        self.artifact_names.append(artifact.name)
        self.artifact_lookup[artifact.name] = artifact

        if artifact.name == "Gridworld":
            self.gridworld = artifact

    def add_event(self, event: Event):
        self.event_handler.add_event(event)

    @staticmethod
    def get_item_class(item):
        return inspect.getmro(type(item))

    def add(self, item):
        """
        Add a new item (agent, artifact, population, event, or a list of valid items) to the environment.

        :param item: Item to be added
        """
        item_class = self.get_item_class(item)

        class_method_mapping = {
            Artifact: self.add_artifact,
            Agent: self.add_agent,
            Population: self.add_population,
            Event: self.add_event,
            list: self.add_list,
        }

        for item_type, method in class_method_mapping.items():
            if item_type in item_class:
                method(item)
                break
        else:
            raise UnsupportedItemType()

    def add_population(self, item):
        for it in item:
            self.add_agent(it)

    def add_list(self, item):
        for it in item:
            self.add(it)

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

        if not self.gridworld:
            gridworld = Gridworld()
            self.add(gridworld)
            self.gridworld = self["Gridworld"]

        # assert that all artifacts have necessary functionality
        self.validate_artifacts()

        # go through the artifacts and set them up
        for name, artifact in self.action_handler.artifacts.items():
            artifact.compile(self)
            self.action_space[artifact.name] = artifact.action_space
            artifact.agents = self.agent_id_lookup

        for agent in self.agents:
            agent.action_space = self.action_space.copy()
            agent.environment = self
            agent.compile()

        self.n_artifacts = len(self.action_handler.artifacts)

        self._is_compiled = True

        if self.database:
            self.cx_socket.sync_environment()

    def reset(self, reset_agents: bool = True, reset_artifacts: bool = True, create_new_agent_queue: bool = True) -> None:
        """
        Resets the environment
        """
        self.log("INFO", "resetting environment")
        if not self.agents or len(self.agents) == 0:
            raise ValueError("agents must be added to the environment before  "
                             "the first step is run")

        if not self._is_compiled:
            self.compile()

        self.current_step = 0
        self.current_episode += 1

        if reset_agents:
            # reset each agent
            for agent in self.agents:
                agent.reset()

        if create_new_agent_queue:
            # add agent to the agent queue
            for agent in self.agents:
                self.agent_queue.append(agent)

        if reset_artifacts:
            for artifact in self.artifacts:
                artifact.reset(self)

        self.gridworld.display()

        if self.use_gui:
            self._backend_while_loop()

        return None

    def update_simulation_state(self):
        self.current_step += 1
        if self.current_step >= self.max_steps:
            self.current_episode += 1
            self.current_step = 0
        if self.current_episode >= self.max_episodes:
            self._should_stop_simulation = True

        if self.use_database:
            self.cx_socket.sync_environment()

    def _match_action_arguments(self, valid_actions, action):
        action_name, action_params = list(action.items())[0]
        action_name = action_name.lower()

        # Get the dataclass for the action
        action_class = valid_actions.get(action_name)

        if not action_class:
            return None, None

        # Get the fields (parameters) of the action dataclass
        dataclass_fields = [field.name for field in fields(action_class)]

        # Map generic parameters to specific dataclass fields
        mapped_params = {}
        for i, field_name in enumerate(dataclass_fields):
            param_key = f"param{i + 1}"
            if param_key in action_params:
                mapped_params[field_name] = action_params[param_key]
            else:
                # Handle missing parameters, possibly with default values
                # For now, raising an error
                raise ValueError(f"Missing parameter '{field_name}' for action '{action_name}'")

        return action_name, mapped_params

    def execute(self, agent, action: Union[dict, Any]) -> Any:
        self.log("INFO", f"{agent.name} is executing action: {action}")
        # Generate a mapping of action names from the agent's action space
        action_names = {(item.__name__.lower()): item for value in agent.action_space.values() for item in value}

        # Initialize the observation to None
        observation = None

        # If action is a dataclass, convert it to dictionary
        if is_dataclass(action):
            action_name = action.__class__.__name__.lower()
            action_params = asdict(action)
        elif isinstance(action, Action):
            # Convert the action to its dictionary representation
            action_dict = action.to_dict()
            action_name = action_dict['name'].lower()  # Convert class name to lowercase
            action_params = action_dict['parameters']
        elif isinstance(action, dict):
            # Extract the action name and parameters
            action_name, action_params = self._match_action_arguments(action_names, action)
        else:
            raise TypeError("action must be either a dataclass or a dictionary")

        # Check if the action exists in the action space
        if action_name in action_names:
            print(action_name, action_params)
            _action = action_names[action_name](**action_params)
            print(_action)
            # Convert the action_params dict to a dataclass instance if it isn't already
            try:
                observation = self.action_handler.process_action(agent, _action)
            except TypeError:
                observation = "Action failed because of error in processing the action in the artifact"
        elif self.strict:
            raise ValueError("")

        agent.add_observation(observation)

        return observation

    def process_turn(self, agent: Agent):
        # Before turn methods
        for func in agent.before_turn_methods:
            func()

        agent.step()

        # After turn methods
        for func in agent.after_turn_methods:
            func()

        if self.use_database:
            self.cx_socket.sync_agent(agent=agent)

    def step(self):
        self._current_time = time.perf_counter()
        self.log("INFO", f"{self.current_episode}: {self.current_step} is executing action:")

        for _ in range(len(self.agent_queue)):
            agent = self.agent_queue.popleft()
            self.process_turn(agent)

        assert len(self.agent_queue) == 0, "Unexpected behavior: Agent queue should be empty"

        for agent in self.agents:
            self.agent_queue.append(agent)

        self.action_handler.step()

        self.update_simulation_state()

        if self.use_gui:
            self._backend_while_loop()

    def _backend_while_loop(self):
        self.cx_socket.sync_environment()
        while self.STATUS == 0:
            time.sleep(0.1)

        if self.STATUS == 2:
            print("status is next")
            self.STATUS = 0

    @property
    def get_status(self):
        sts = self.STATUS
        return ENV_STATUS.get(sts, "Unknown")

    @property
    def metadata(self):
        # Basic attributes
        env_dict = {
            "name": self.name,
            "verbose": self.verbose,
            "seed": self.seed,
            "use_gui": self.use_gui,
            "currentStep": self.current_step,
            "maxSteps": self.max_steps,
            "currentEpisode": self.current_episode,
            "maxEpisodes": self.max_episodes,
            "step_delay": self.step_delay,
            "n_agents": self.n_agents,
            "n_artifacts": self.n_artifacts,
            "strict": self.strict,
            "status": ENV_STATUS.get(self.STATUS, "Unknown"),
            "x_size": self.x_size,
            "y_size": self.y_size,
            "agentQueue": [agent.name for agent in list(self.agent_queue)]
        }

        return env_dict

    @property
    def agent_metadata(self):
        agent_data = {}
        for agent in self.agents:
            agent_data[agent.name] = agent.to_dict()
        return agent_data

    @property
    def artifact_metadata(self):
        artifact_data = {}
        for artifact in self.artifacts:
            artifact_data[artifact.name] = artifact.to_dict()
        return artifact_data

    def get(self, item, output_format: str = None):
        pass

    def action_logs(self):
        return self.action_handler.action_logs

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

    def handle_button_event(self, action: str):
        if action == "next":
            self.STATUS = 2
        if action == "pause":
            self.STATUS = 0
        if action == "play":
            self.STATUS = 1
        self.cx_socket.sync_environment()

    @property
    def agent_queue_length(self):
        return len(self.agent_queue)

    def log(self, level: Union[int, str], msg: str, *args, **kwargs):
        """
        Convenience method for logging messages.

        :param level: The logging level, either as a string or an integer.
        :param msg: The format string for the message.
        :param args: The arguments to merge into msg.
        :param kwargs: Other keyword arguments.
        """
        # Map string levels to their numeric values
        str_to_level = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

        # Convert string level to numeric if necessary
        if isinstance(level, str):
            level = str_to_level.get(level.upper(), logging.INFO)  # Default to INFO if level is unrecognized

        # Log the message
        self.logger.log(level, msg, *args, **kwargs)

        if self.use_database:
            CxLogs().add(
                timestamp=datetime.datetime.utcnow(),
                level=level,
                msg=msg
            )

            CxLogs().emit(self.cx_socket.socketio)

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
