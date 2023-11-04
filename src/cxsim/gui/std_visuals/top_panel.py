import random

import dearpygui.dearpygui as dpg


class TopPanel:
    def __init__(self, visualizer, environment, dimension_config):
        self.visualizer = visualizer
        self.environment = environment
        self.dimension_config = dimension_config
        self.HEIGHT = dimension_config.top_panel_height
        self.WIDTH = dimension_config.top_panel_width
        self.pos_y = 0
        self.panel = None

        self.text_size = 10

        # environment group
        self.env_group = None
        self.env_group_width = int(self.WIDTH * 0.3)
        self.environment_name_text_uuid = dpg.generate_uuid()
        self.current_step_uuid = dpg.generate_uuid()
        self.n_agents_text_uuid = dpg.generate_uuid()
        self.n_artifacts_text_uuid = dpg.generate_uuid()

        # control group
        self.control_group = None
        self.pause_button = None
        self.play_button = None
        self.next_step = None
        self.control_group_width = int(self.WIDTH * 0.3)

        # current status group
        self.current_state_group = None
        self.current_state_group_width = int(self.WIDTH * 0.3)
        self.environment_status = None
        self.current_task = None
        self.current_status_dpg_uuid = dpg.generate_uuid()
        self.current_task_dpg_uuid = dpg.generate_uuid()

        self.progress_bar_uuid = dpg.generate_uuid()


    def pause_simulation_callback(self, sender):
        self.visualizer.is_paused = True
        self.environment_status = "Paused"

    def resume_simulation_callback(self, sender):
        self.visualizer.is_paused = False
        self.environment_status = f"Running step {self.environment.current_step} (Running)"

    def skip_simulation_callback(self, sender):
        self.visualizer.skip_steps = 1
        self.environment_status = f"Running step {self.environment.current_step} (Skipping)"

    def render(self):
        # env group
        dpg.set_value(self.current_step_uuid, f"Current step: {self.environment.current_step} / {self.environment.max_steps}")
        dpg.set_value(self.n_agents_text_uuid, f"Number of Agents: {self.environment.n_agents}")
        dpg.set_value(self.n_artifacts_text_uuid, f"Number of Artifacts: {self.environment.n_artifacts}")
        dpg.set_value(self.progress_bar_uuid, (self.environment.n_agents - len(self.environment.agent_queue)) / self.environment.n_agents)
        # control group

        # status group
        dpg.set_value(self.current_status_dpg_uuid, f"Status: {self.environment_status}")
        dpg.set_value(self.current_task_dpg_uuid, f"Task: {self.current_task}")

    def resize(self):
        self.env_group_width = int(self.dimension_config.top_panel_width * 0.3)
        self.control_group_width = int(self.dimension_config.top_panel_width * 0.3)
        self.current_state_group_width = int(self.dimension_config.top_panel_width * 0.3)

        dpg.set_item_height(self.panel, self.dimension_config.top_panel_height)
        dpg.set_item_width(self.panel, self.dimension_config.top_panel_width)

        dpg.set_item_width(self.env_group, self.env_group_width)
        dpg.set_item_width(self.control_group, self.control_group_width)
        dpg.set_item_width(self.current_state_group, self.current_state_group_width)

    def create(self):
        with dpg.window(
            label="Top Panel",
            tag="panel",
            pos=(0, 0),
            height=self.HEIGHT,
            width=self.WIDTH,
            no_close=True,
            no_move=True,
            menubar=False,
            no_scrollbar=True,
            no_collapse=True,
            no_resize=True,
            no_title_bar=True,
        ) as self.panel:
            with dpg.group(horizontal=True):
                with dpg.group(width=self.env_group_width) as self.env_group:
                    self.environment_name_text_uuid = dpg.add_text(f"Environment name: {self.environment.name}")
                    self.current_step_uuid = dpg.add_text(f"Current step: {self.environment.current_step} / {self.environment.max_steps}")
                    self.n_agents_text_uuid = dpg.add_text(f"Number of Agents: {self.environment.n_agents}")
                    self.n_artifacts_text_uuid = dpg.add_text(f"Number of Artifacts: {self.environment.n_artifacts}")

                with dpg.group(horizontal=False) as self.control_group:
                    self.next_step = dpg.add_button(
                        label="Next Step",
                        callback=self.skip_simulation_callback,
                    )
                    self.play_button = dpg.add_button(
                        label="Resume",
                        callback=self.resume_simulation_callback,
                    )
                    self.pause_button = dpg.add_button(
                        label="Pause",
                        callback=self.pause_simulation_callback,
                    )

                with dpg.group() as self.current_state_group:
                    self.current_status_dpg_uuid = dpg.add_text(f"Status: {self.environment_status}")
                    self.current_task_dpg_uuid = dpg.add_text(f"Task: {self.current_task}")
                    self.progress_bar_uuid = dpg.add_progress_bar(label="Progress bar", default_value=0.2)
