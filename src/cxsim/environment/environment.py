import time
import logging

import numpy as np
import names
import dearpygui.dearpygui as dpg

from src.cxsim.agents.agent import Agent
from src.cxsim.agents.population import Population
from src.cxsim.artifacts.artifact import Artifact
from src.cxsim.actions.action_handler import ActionHandler
from src.cxsim.queries.query_handler import QueryHandler
from src.cxsim.gui.visualizer import Visualizer
from src.cxsim.utilities.background_jobs.background_task import BackgroundTask
from src.cxsim.environment.calander import Calender
from src.cxsim.agents.item import ItemHandler
from src.cxsim.actions.standard import Skip

from src.cxsim.prompts.prompt import ObservationPrompt, InitializationPrompt


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
        gui: bool = False,
        verbose: int = 0,
        seed: int = None,
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
        self.gui = gui
        self.start_time = None

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

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

        self.max_queries = 1
        self.max_actions = 1
        self.action_space = {}
        self.query_space = {}

        # artifacts
        self.n_artifacts = 0
        self.artifacts = []
        self.artifact_lookup = {}

        self.action_handler = ActionHandler(self)
        self.query_handler = QueryHandler(self)

        self.calender = Calender()
        self.item_handler = ItemHandler(self)

        if self.gui:
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
        self.action_handler.add_artifact(artifact)
        self.query_handler.add_artifact(artifact)
        self.artifacts.append(artifact)
        self.artifact_lookup[artifact.name] = artifact

        if artifact.name == "Gridworld":
            self.visualizer.world.blocks = artifact.x_size

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
            pass

    def validate_artifacts(self):
        for name, artifact in self.action_handler.artifacts.items():
            assert artifact.set_up.__code__ != Artifact.process_query.__code__, "process_query method must be implemented by subclass"

            assert artifact.reset.__code__ != Artifact.reset.__code__, "process_query method must be implemented by subclass"

            assert artifact.process_action.__code__ != Artifact.process_action.__code__, "process_action method must be implemented by subclass"

            assert artifact.process_query.__code__ != Artifact.process_query.__code__, "process_query method must be implemented by subclass"

    def _construct_system_prompt(self, agent: Agent):


        # Setting variables for the agent's prompt sections
        agent.prompt.set_variable("name", agent.name, "Agent information")

        # Inventory
        agent.prompt.set_variable("inventory", str(agent.inventory.starting_inventory), "Agent information")

        # Action Restrictions
        formatted_action_restrictions = agent.prompt.sections["Action Restrictions"].format_list(
            agent.action_restrictions)
        agent.prompt.set_variable("action_restrictions", formatted_action_restrictions, "Action Restrictions")

        # Environment Information
        agent.prompt.set_variable("n_agents", str(len(self.agents)), "Environment information")
        agent.prompt.set_variable("max_steps", str(self.max_steps), "Environment information")

        # Artifacts
        num_artifacts = len(self.action_handler.artifacts)
        agent.prompt.set_variable("num_artifacts", str(num_artifacts), "Artifact information")
        agent.prompt.set_artifact_descriptions(self.artifacts)

        # Assuming global actions are a list
        formatted_global_actions = agent.prompt.format_list(["""act(action="Skip", parameters=["None"])"""])
        agent.prompt.set_variable("global_actions", formatted_global_actions, "Action space")

        agent.prompt.set_variable("current_position", str((agent.x_pos, agent.y_pos)))
        agent.prompt.set_variable("goal", "Go to the bottom left")

        agent.set_up()

    def prepare(self):
        self.start_time = time.perf_counter()
        # assert that all agents have necessary functionality
        self.validate_agents()

        # assert that all artifacts have necessary functionality
        self.validate_artifacts()

        # go through the artifacts and set them up
        for name, artifact in self.action_handler.artifacts.items():
            artifact.set_up(self)

            self.action_space[artifact.name] = artifact.get_action_space()

            self.query_space[artifact.name] = artifact.get_query_space()

            artifact.agents = self.agent_id_lookup

            for agent in self.agents:
                agent.action_space = self.action_space.copy()
                agent.query_space = self.query_space.copy()
                self._construct_system_prompt(agent)

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

        if self.gui:
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

    def process_turn(self, agent: Agent):
        for func in agent.before_turn_methods:
            func()

        n_queries = 0
        n_actions = 0

        while n_actions < agent.max_actions and n_queries < agent.max_queries:
            observation_prompt = ObservationPrompt()
            observation_prompt.set_current_step(str(self.current_step))
            observation_prompt.set_inventory(str(agent.display_inventory()))
            observation_prompt.set_working_memory(agent.working_memory.content)
            observation_prompt.set_current_map(self.artifact_lookup["Gridworld"].to_text(special_agent=agent))
            observation_prompt.set_current_position(str((agent.x_pos, agent.y_pos)))

            agent.add_message("user", observation_prompt.content)

            with BackgroundTask(agent.execute_action, self.visualizer, agent_name=agent.name):
                pass

            if len(agent.action_queue) == 0:
                self.log(logging.WARNING, f"Agent {agent.name, agent.id} did not have an action in the action_queue")
                agent.action_queue.append({"action": "Skip", "parameters": ["None"], "memory": "Skipped turn"})

            action = agent.action_queue.pop(0)
            self.log(logging.INFO, str(agent) + " " + str(action))

            action_names = {(item.__name__.lower()): item.__name__ for value in agent.action_space.values() for item in value}

            if action["action"].lower() in action_names:
                action["action"] = action_names[action["action"].lower()]
                self.action_handler.process_action(agent, action)
                n_actions += 1
            else:
                observation = self.query_handler.process_query(agent, action)
                if observation is None:
                    n_actions += 1
                    observation = "skip was successful"
                agent.add_message("function", observation, function_name="act")
                n_queries += 1

        agent.step()

        for func in agent.after_turn_methods:
            func()

    def step(self) -> [np.ndarray, list, list]:
        if self.gui:
            if self.visualizer.skip_steps > 0:
                self.visualizer.top_panel.environment_status = "Skipping Step"
                self.visualizer.skip_steps -= 1
                self.visualizer.step(True)
            else:
                self.visualizer.top_panel.environment_status = "Paused"
                while (time.perf_counter() - self._current_time <= self.step_delay) or self.visualizer.is_paused:
                    self.visualizer.step(False)
                    if self.visualizer.skip_steps != 0:
                        self.visualizer.skip_steps -= 1
                        break
                else:
                    self.visualizer.top_panel.environment_status = "Running"
                    self.visualizer.step(True)

        self._current_time = time.perf_counter()

        # execute actions for each agent all actions are processed
        num_tokens = []
        for agent in self.agents:
            self.process_turn(agent)

        self.action_handler.step()

        # should simulation stop based on response from artifacts
        should_continue = self.action_handler.should_continue()

        self.update_simulation_state()
        return should_continue

    def action_logs(self):
        return self.action_handler.action_logs

    def is_running(self):
        if self.gui:
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
