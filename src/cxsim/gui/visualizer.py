import dearpygui.dearpygui as dpg

from src.cxsim.gui.tabs.market_tab import MarketplaceTab
from src.cxsim.gui.agent_overview import AgentOverview
from src.cxsim.gui.worldview import World
from src.cxsim.gui.top_panel import TopPanel
from src.cxsim.gui.logs_popup_window import LogsWindow
from src.cxsim.utilities.background_jobs.job_manager import JobManager
from src.cxsim.gui.assets.path_definition import ASSET_PATH

import time

dpg.create_context()

artifact_tabs = {
    "Marketplace": MarketplaceTab()
}


color_dict = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
    'brown': (165, 42, 42),
    'gray': (128, 128, 128),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}


class GUI:
    def __init__(self, close_on_finish: bool = False):
        self.environment = None
        self.close_on_finish = close_on_finish
        self.WIDTH = 1400
        self.HEIGHT = 1000

        self.agent_world_height = int(self.HEIGHT * 0.8)
        self.agent_world_width = int(3 * self.WIDTH / 5)

        self.info_tab_height = self.HEIGHT
        self.info_tab_width = int(self.WIDTH / 3)
        self.text_control = None

        self.middle_line = int(self.WIDTH / 2) + int(self.WIDTH * 0.01)
        self.top_position = 20

        self.environment_overview_text = dpg.generate_uuid()
        self.agent_overview_text = dpg.generate_uuid()
        self.agent_information_text = dpg.generate_uuid()
        self.environment_date = dpg.generate_uuid()
        self.agent_information_table = {}
        self.agent_interaction_table = {}
        self.action_log_size = 30
        self.action_logs = [["N/A" for _ in range(4)] for _ in range(self.action_log_size)]

        self.artifact_names = []
        self.show_artifacts = []

        self.current_tab = None
        self.show_environment_overview = False
        self.show_agent_overview = False
        self.last_environment_step = 0

        self.is_paused = True
        self.skip_steps = 0

        self.show_agent_name = None

        self.show_agent_header = None
        self.show_agent_inventory = None
        self.show_agent_messages = None

        self.agent_inventory = None

        self.last_key_input = None

        self.agent_overview = None
        self.world = None
        self.top_panel = None
        self.log_window = None

        self.job_manager = JobManager()
        self.background_tasks_exist = False

    def draw_interaction(self, source_agent, target_agent, color, tag: str = None):
        if tag is None:
            return dpg.draw_line((source_agent.x_pos, source_agent.y_pos), (target_agent.x_pos, target_agent.y_pos), color=color_dict[color])
        else:
            return dpg.draw_line((source_agent.x_pos, source_agent.y_pos), (target_agent.x_pos, target_agent.y_pos),
                                 color=color_dict[color], tag=tag, show=False)

    def draw_adjacency_matrix(self):
        mat = self.environment.artifact_controller.artifacts["Market"].get_adjacency_matrix()
        for source_idx, source_agent in enumerate(self.environment.agents):
            for target_idx, target_agent in enumerate(self.environment.agents):
                try:
                    if mat[source_idx][target_idx] == 1:
                        dpg.show_item(self.agent_interaction_table[source_agent.id][target_agent.id])
                    elif source_agent != target_agent:
                        dpg.hide_item(self.agent_interaction_table[source_agent.id][target_agent.id])
                except Exception as e:
                    print(e)
                    print(source_agent, source_idx, target_agent, target_idx)
                    raise Warning()

    def step(self, is_new_step):
        dpg.render_dearpygui_frame()
        dpg.set_value(self.environment_overview_text, f"episode: {self.environment.current_episode} / {self.environment.max_episodes}\nstep: {self.environment.current_step} / {self.environment.max_steps}")
        dpg.set_value(self.environment_date, f"date: {self.environment.calender.current_date}")
        self.update()
        if is_new_step:
            self.agent_overview.update()
        for name, artifact_tab in artifact_tabs.items():
            if name in self.environment.action_handler.artifacts.keys():
                artifact_tab.step()
        dpg.render_dearpygui_frame()

    def is_running(self):
        return dpg.is_dearpygui_running()

    def input_text_callback(self, sender, app_data):
        self.last_key_input = app_data

    def draw_action_logs(self):
        with dpg.child_window(label="Action Logs", show=False) as self.actions:
            with dpg.table(header_row=True):
                # use add_table_column to add columns to the table,
                # table columns use child slot 0
                dpg.add_table_column(label="step")
                dpg.add_table_column(label="agent")
                dpg.add_table_column(label="artifact")
                dpg.add_table_column(label="action")
                for i in range(len(self.environment.action_handler.action_logs)):
                    with dpg.table_row():
                        for j in range(0, 4):
                            action = self.environment.action_handler.action_logs[i]
                            self.action_logs[i][j] = dpg.add_text(action[j], wrap=110)

    def draw_environment_overview(self):
        with dpg.child_window(label="Environment Overview", show=self.show_environment_overview) as self.environment_overview:
            self.environment_date = dpg.add_text("", wrap=300)
            self.environment_overview_text = dpg.add_text("", wrap=300)

    def show_callback(self, sender):
        if sender == "show_overview":
            self.switch_tab(self.current_tab, self.environment_overview)
        elif sender == "show_actions":
            self.switch_tab(self.current_tab, self.actions)
        elif sender == "agent_overview":
            self.switch_tab(self.current_tab, self.agent_overview)
        elif sender == "show_log_popup":
            self.switch_tab(self.current_tab, self.log_window)
        elif sender in artifact_tabs.keys():
            self.switch_tab(self.current_tab, artifact_tabs[sender].get_window())

    def switch_tab(self, previous_tab, next_tab):
        # if a previous tab exists, hide it
        if previous_tab == self.agent_overview:
            self.agent_overview.set_show(False)
        elif previous_tab == self.log_window:
            self.log_window.set_show(False)

        elif previous_tab:
            dpg.hide_item(previous_tab)

        if next_tab == self.agent_overview:
            self.agent_overview.set_show(True)
        elif next_tab == self.log_window:
            self.log_window.set_show(True)
        else:
            dpg.show_item(next_tab)

        self.current_tab = next_tab

    def create_information_window(self):
        self.artifact_names = list(self.environment.action_handler.artifacts.keys())
        with dpg.window(
            label="Information", tag="Info",
            height=self.info_tab_height,
            width=self.info_tab_width,
            pos=(self.agent_world_width + int(self.WIDTH * 0.01), 0),
            no_close=True, no_move=True,
            no_scrollbar=True,
            no_collapse=True,
            no_resize=True,
            no_title_bar=True
        ) as self.info:
            with dpg.menu_bar(label="Information menu bar"):
                with dpg.menu(label="Environment"):
                    dpg.add_menu_item(label="Overview", tag="show_overview", callback=self.show_callback)
                    dpg.add_menu_item(label="Actions", tag="show_actions", callback=self.show_callback)

                dpg.add_menu_item(label="Agents", tag="agent_overview", callback=self.show_callback)

                with dpg.menu(label="Artifacts"):
                    for artifact_name in self.artifact_names:
                        dpg.add_menu_item(label=artifact_name, tag=artifact_name, callback=self.show_callback)

                dpg.add_menu_item(label="Settings")

                dpg.add_menu_item(label="Logs", tag="show_log_popup", callback=self.show_callback)

            self.draw_environment_overview()
            self.draw_action_logs()
            self.agent_overview.draw()
            self.log_window.draw()

            for artifact_name in self.artifact_names:
                if artifact_name in artifact_tabs.keys():
                    artifact_tabs[artifact_name].draw()

    def prepare(self, environment):
        self.environment = environment
        self.agent_overview = AgentOverview(environment)
        self.world = World(environment, self.WIDTH, self.HEIGHT)
        self.world.blocks = environment.starting_block_size
        self.top_panel = TopPanel(self, environment, self.HEIGHT, self.WIDTH)
        self.log_window = LogsWindow(environment)

    def reset(self, environment):
        self.environment = environment
        if "Gridworld" in self.environment.artifact_lookup.keys():
            print(self.environment.artifact_lookup["Gridworld"].x_size)
            self.world.blocks = self.environment.artifact_lookup["Gridworld"].x_size

        for name, artifact in artifact_tabs.items():
            artifact.reset(environment)

        self.start()

    def update(self):
        self.world.update()
        self.top_panel.update()
        #self.agent_overview.update()

    def run_event_loop(self, current_time):
        if self.skip_steps > 0:
            self.top_panel.environment_status = "Skipping Step"
            self.skip_steps -= 1
            self.step(True)
        else:
            self.top_panel.environment_status = "Paused"
            while (time.perf_counter() - current_time <= self.environment.step_delay) or self.is_paused:
                self.step(False)
                if self.skip_steps != 0:
                    self.skip_steps -= 1
                    break
            else:
                self.top_panel.environment_status = "Running"
                self.step(True)

    def resize(self):
        self.WIDTH = dpg.get_viewport_width()
        self.HEIGHT = dpg.get_viewport_height()

        self.info_tab_height = self.HEIGHT
        self.info_tab_width = int(2 * self.WIDTH / 5)

        dpg.set_item_width(self.info, self.info_tab_width)
        dpg.set_item_height(self.info, self.info_tab_height)

        dpg.set_item_pos(self.info, [int(3 * self.WIDTH / 5), 0])

        self.world.resize()
        self.top_panel.resize()
        self.agent_overview.resize()

    def start(self):
        self.top_panel.create()
        self.create_information_window()
        self.world.create()

        with dpg.theme() as item_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (200, 200, 100), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)

        dpg.set_viewport_resize_callback(self.resize)
        dpg.create_viewport(
            title='PyCxsim',
            width=self.WIDTH,
            height=self.HEIGHT,
            small_icon=ASSET_PATH.joinpath("large_icon.ico").__str__(),
            large_icon=ASSET_PATH.joinpath("large_icon.ico").__str__()
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()

    def __del__(self):
        dpg.destroy_context()



