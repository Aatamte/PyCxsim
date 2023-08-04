import dearpygui.dearpygui as dpg
import math
from src.new_visualization.tabs.market_tab import MarketTab

dpg.create_context()

artifact_tabs = {
    "Market": MarketTab()
}


class EnvironmentOverview:
    def __init__(self):
        pass

    def create(self):
        pass

    def updated(self):
        pass


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

        self.bottom_panel_height = int(self.HEIGHT * 0.12)
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
        self.last_environment_step = 0

        self.is_paused = True

    def draw_interaction(self, source_agent, target_agent, color, tag: str = None):
        if tag is None:
            return dpg.draw_line((source_agent.x_pos, source_agent.y_pos), (target_agent.x_pos, target_agent.y_pos), color=color_dict[color])
        else:
            return dpg.draw_line((source_agent.x_pos, source_agent.y_pos), (target_agent.x_pos, target_agent.y_pos),
                                 color=color_dict[color], tag=tag, show=False)

    def update_agent_overview(self):
        #dpg.set_value(self.agent_overview_text, f"current episode: {self.environment.current_step}")
        for agent in self.environment.agents:
            #agent_str = f"capital: {agent.capital}\ninventory: {agent.inventory}"
            #dpg.set_value(self.agent_information_table[agent.name], agent_str)
            pass
        for idx, action in enumerate(self.environment.action_logs()[-self.action_log_size:]):
            dpg.set_value(self.action_logs[idx][0], str(self.environment.current_step))
            dpg.set_value(self.action_logs[idx][1], action[0].name)
            dpg.set_value(self.action_logs[idx][2], str(action[1]))

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
        dpg.set_value(self.environment_date,f"date: {self.environment.calender.current_date}")
        self.update_agent_overview()
        if is_new_step:
            for name, artifact in artifact_tabs.items():
                artifact.step()
        self.draw_adjacency_matrix()
        dpg.render_dearpygui_frame()

    def is_running(self):
        return dpg.is_dearpygui_running()

    def draw_world(self):
        num_agents = len(self.environment.agents)
        radius = num_agents * 4
        with dpg.drawlist(width=self.agent_world_width, height=self.agent_world_height):
            for idx, agent in enumerate(self.environment.agents):
                self.agent_interaction_table[agent.id] = {}
                angle = math.pi * 2 * idx / num_agents
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                agent.x_pos = x + self.agent_world_middle_position[0]
                agent.y_pos = y + int(radius * 1.2)
                dpg.draw_circle((agent.x_pos, agent.y_pos), 10, color=[0, 255, 0], fill=[0, 255, 0])
                for target_idx, target_agent in enumerate(self.environment.agents):
                    if target_agent != agent:
                            self.agent_interaction_table[agent.id][target_agent.id] = self.draw_interaction(self.environment.agents[idx], self.environment.agents[target_idx], "red", tag=f"{agent.id}_{target_agent.id}")

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
            #self.draw_agent_overview()

    def draw_agent_overview(self):
        with dpg.collapsing_header(label="Agent Overview", default_open=False):
            self.agent_overview_text = dpg.add_text("", wrap=300)
            self.add_agent_information_table()

    def add_agent_information_table(self):
        with dpg.collapsing_header(label="Agent information", default_open=False):
            self.agent_information_text = dpg.add_text("", wrap=300)
            for agent in self.environment.agents:
                self.agent_information_table[agent.name] = dpg.generate_uuid()
                with dpg.collapsing_header(label=agent.name, default_open=False):
                    self.agent_information_table[agent.name] = dpg.add_text("", wrap=300)

        with dpg.drawlist(width=self.agent_world_width, height=self.agent_world_height):
            for source_agent in self.environment.agents:
                self.agent_interaction_table[source_agent.name] = {}
                #for target_agent in self.environment.agents:
                    #if source_agent != target_agent:
                  #      self.agent_interaction_table[source_agent.name][target_agent.name] = dpg.generate_uuid()
                   #     self.draw_interaction(source_agent, target_agent, "gray")

    def show_callback(self, sender):
        print(sender)
        if sender == "show_overview":
            self.switch_tab(self.current_tab, self.environment_overview)
        elif sender == "show_logs":
            self.switch_tab(self.current_tab, self.env_logs)
        elif sender in artifact_tabs.keys():
            self.switch_tab(self.current_tab, artifact_tabs[sender].get_window())

    def switch_tab(self, previous_tab, next_tab):
        # if a previous tab exists, hide it
        if previous_tab:
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
            no_resize=True
        ) as info:
            self.info = info
            with dpg.menu_bar(label="Information menu bar"):
                with dpg.menu(label="Environment"):
                    dpg.add_menu_item(label="Overview", tag="show_overview", callback=self.show_callback)
                    dpg.add_menu_item(label="logs", tag="show_logs", callback=self.show_callback)

                with dpg.menu(label="Artifacts"):
                    for artifact_name in self.artifact_names:
                        dpg.add_menu_item(label=artifact_name, tag=artifact_name, callback=self.show_callback)
                dpg.add_menu_item(label="Agents")
                dpg.add_menu_item(label="Settings")

            self.draw_environment_overview()
            self.draw_action_logs()

            for artifact_name in self.artifact_names:
                if artifact_name in artifact_tabs.keys():
                    artifact_tabs[artifact_name].draw()

    def pause_simulation_callback(self, sender):
        self.is_paused = True

    def resume_simulation_callback(self, sender):
        self.is_paused = False

    def draw_bottom_panel(self):
        with dpg.child_window(
            label="Bottom Panel", tag="Bottom",
            width=self.bottom_panel_width,
            height=self.bottom_panel_height,
            pos=(50, self.agent_world_height)
        ) as bottom:
            self.bottom = bottom
            dpg.add_text("Control Panel")
            dpg.add_button(label="Pause", pos=(0, 40), callback=self.pause_simulation_callback, height=50, width=50)
            dpg.add_button(label="Resume", pos=(55, 40), callback=self.resume_simulation_callback, height=50, width=50)

    def create_world_window(self):
        with dpg.window(
            label="Environment",
            tag="World",
            height = self.HEIGHT,
            no_close=True,
            no_move=True,
            menubar=True,
            no_scrollbar=True,
            no_collapse=True,
            no_resize=True
        ) as world:
            self.world = world
            dpg.add_spacer(height=self.top_position)
            self.draw_world()
            self.draw_bottom_panel()

    def reset(self, environment):
        self.environment = environment
        for name, artifact in artifact_tabs.items():
            artifact.reset(environment)
        self.start()

    def update(self):
        self.WIDTH = dpg.get_viewport_width()
        self.HEIGHT = dpg.get_viewport_height()

        self.agent_world_height = self.HEIGHT
        self.agent_world_width = int(2 * self.WIDTH / 3)
        self.agent_world_middle_position = (int(self.agent_world_width / 2), int(self.agent_world_height / 2))

        self.info_tab_height = self.HEIGHT
        self.info_tab_width = int(self.WIDTH / 3)

        self.bottom_panel_height = int(self.HEIGHT * 0.2)
        self.bottom_panel_width = int(2 * self.WIDTH / 3)

        dpg.set_item_width(self.world, self.agent_world_width)
        dpg.set_item_width(self.info, self.info_tab_width)

        dpg.set_item_height(self.world, self.agent_world_height)
        dpg.set_item_height(self.info, self.info_tab_height)

        dpg.set_item_pos(self.info, [self.agent_world_width, 0])

    def start(self):
        self.create_world_window()
        self.create_information_window()

        with dpg.handler_registry():
            pass
            #dpg.add_mouse_move_handler(callback=self.update_plot_data, user_data=self.plot_data)

        with dpg.theme() as item_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (200, 200, 100), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)

        dpg.bind_item_theme(self.bottom, item_theme)

        dpg.set_viewport_resize_callback(self.update)
        dpg.create_viewport(title='Complex Adaptive Economic Simulator', width=self.WIDTH, height=self.HEIGHT)
        dpg.setup_dearpygui()
        dpg.show_viewport()

    def __del__(self):
        dpg.destroy_context()



