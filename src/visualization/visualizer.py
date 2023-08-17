import dearpygui.dearpygui as dpg
import math
from src.visualization.tabs.market_tab import MarketplaceTab
from src.visualization.agent_overview import AgentOverview
from src.visualization.worldview import World
from src.visualization.bottom_panel import BottomPanel

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


class Visualizer:
    def __init__(self, environment):
        self.environment = environment
        self.WIDTH = 1400
        self.HEIGHT = 1000

        self.world_height = 120
        self.world_width = 120

        self.agent_world_height = int(self.HEIGHT * 0.8)
        self.agent_world_width = int(2 * self.WIDTH / 3)
        self.agent_world_middle_position = (int(self.agent_world_width / 2), int(self.agent_world_height / 2))

        self.info_tab_height = self.HEIGHT
        self.info_tab_width = int(self.WIDTH / 3)
        self.text_control = None

        self.bottom_panel_height = int(self.HEIGHT * 0.2)
        self.bottom_panel_width = int(2 * self.WIDTH / 3)

        self.middle_line = int(self.WIDTH / 2) + int(self.WIDTH * 0.01)
        self.top_position = 20

        self.environment_overview_text = dpg.generate_uuid()
        self.agent_overview_text = dpg.generate_uuid()
        self.agent_information_text = dpg.generate_uuid()
        self.environment_date = dpg.generate_uuid()
        self.agent_information_table = {}
        self.agent_interaction_table = {}
        self.action_log_size = 30
        self.action_logs = [["N/A" for _ in range(3)] for _ in range(self.action_log_size)]

        self.artifact_names = []
        self.show_artifacts = []

        self.current_tab = None
        self.show_environment_overview = False
        self.show_agent_overview = False
        self.last_environment_step = 0

        self.is_paused = True

        self.show_agent_name = None

        self.show_agent_header = None
        self.show_agent_inventory = None
        self.show_agent_messages = None

        self.agent_inventory = None

        self.agent_overview = AgentOverview(environment)
        self.world = World(environment, self.WIDTH, self.HEIGHT)
        self.bottom_panel = BottomPanel(self, environment, self.HEIGHT, self.WIDTH)

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
        dpg.set_value(self.environment_overview_text, f"episode: {self.environment.current_episode} / {self.environment.max_episodes}\nstep: {self.environment.current_step} / {self.environment.max_steps}")
        dpg.set_value(self.environment_date, f"date: {self.environment.calender.current_date}")
        self.world.update()
        if is_new_step:
            for name, artifact_tab in artifact_tabs.items():
                artifact_tab.step()
            #self.agent_overview.update()
        dpg.render_dearpygui_frame()

    def is_running(self):
        return dpg.is_dearpygui_running()

    def draw_action_logs(self):
        with dpg.child_window(label="Action Logs", show=False) as self.env_logs:
            with dpg.table(header_row=True):
                # use add_table_column to add columns to the table,
                # table columns use child slot 0
                dpg.add_table_column(label="step")
                dpg.add_table_column(label="agent")
                dpg.add_table_column(label="action")
                for i in range(self.action_log_size):
                    with dpg.table_row():
                        for j in range(0, 3):
                            self.action_logs[i][j] = dpg.add_text(self.action_logs[i][j], wrap=110)

    def draw_environment_overview(self):
        with dpg.child_window(label="Environment Overview", show=self.show_environment_overview) as self.environment_overview:
            self.environment_date = dpg.add_text("", wrap=300)
            self.environment_overview_text = dpg.add_text("", wrap=300)

    def show_callback(self, sender):
        if sender == "show_overview":
            self.switch_tab(self.current_tab, self.environment_overview)
        elif sender == "show_logs":
            self.switch_tab(self.current_tab, self.env_logs)
        elif sender == "agent_overview":
            if self.current_tab:
                dpg.hide_item(self.current_tab)
            self.agent_overview.set_show(True)
            self.current_tab = self.agent_overview
        elif sender in artifact_tabs.keys():
            self.switch_tab(self.current_tab, artifact_tabs[sender].get_window())

    def switch_tab(self, previous_tab, next_tab):
        # if a previous tab exists, hide it
        if previous_tab == self.agent_overview:
            self.agent_overview.set_show(False)
        elif previous_tab:
            dpg.hide_item(previous_tab)

        dpg.show_item(next_tab)

        self.current_tab = next_tab

    def create_information_window(self):
        self.artifact_names = list(self.environment.artifact_controller.artifacts.keys())
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
        ) as info:
            self.info = info
            with dpg.menu_bar(label="Information menu bar"):
                with dpg.menu(label="Environment"):
                    dpg.add_menu_item(label="Overview", tag="show_overview", callback=self.show_callback)
                    dpg.add_menu_item(label="Agents", tag="agent_overview", callback=self.show_callback)
                    dpg.add_menu_item(label="logs", tag="show_logs", callback=self.show_callback)

                with dpg.menu(label="Artifacts"):
                    for artifact_name in self.artifact_names:
                        dpg.add_menu_item(label=artifact_name, tag=artifact_name, callback=self.show_callback)
                dpg.add_menu_item(label="Settings")

            self.draw_environment_overview()
            self.draw_action_logs()
            self.agent_overview.draw()

            for artifact_name in self.artifact_names:
                if artifact_name in artifact_tabs.keys():
                    artifact_tabs[artifact_name].draw()

    def reset(self, environment):
        self.environment = environment
        for name, artifact in artifact_tabs.items():
            artifact.reset(environment)
        self.start()

    def update(self):
        self.WIDTH = dpg.get_viewport_width()
        self.HEIGHT = dpg.get_viewport_height()

        self.info_tab_height = self.HEIGHT
        self.info_tab_width = int(self.WIDTH / 3)

        dpg.set_item_width(self.info, self.info_tab_width)
        dpg.set_item_height(self.info, self.info_tab_height)

        dpg.set_item_pos(self.info, [int(2 * self.WIDTH / 3), 0])

        self.world.update()
        self.bottom_panel.update()

    def start(self):
        self.bottom_panel.create()
        self.create_information_window()
        self.world.create()

        with dpg.handler_registry():
            pass

        with dpg.theme() as item_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (200, 200, 100), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)

        dpg.set_viewport_resize_callback(self.update)
        dpg.create_viewport(title='Complex Adaptive Economic Simulator', width=self.WIDTH, height=self.HEIGHT)
        dpg.setup_dearpygui()
        dpg.show_viewport()

    def __del__(self):
        dpg.destroy_context()



