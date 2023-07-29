import random

import dearpygui.dearpygui as dpg
from math import sin
import math
import numpy as np

dpg.create_context()


class DataValues():
    clicks = 0


def print_me(sender):
    print(f"Menu Item: {sender}")


def clickMe_callback(sender, value, user_data):
    # increment clickCount
    DataValues.clicks += 1

    # update text
    dpg.set_value(user_data, f"clicks: {DataValues.clicks}")


data = DataValues()


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
        self.WIDTH = 1200
        self.HEIGHT = 1000

        self.world_height = 120
        self.world_width = 120

        self.agent_world_height = self.HEIGHT
        self.agent_world_width = int(2 * self.WIDTH / 3)
        self.agent_world_middle_position = (int(self.agent_world_width / 2), int(self.agent_world_height / 2))

        self.info_tab_height = self.HEIGHT
        self.info_tab_width = int(self.WIDTH / 3)
        self.text_control = None

        self.plot_data = []

        self.middle_line = int(self.WIDTH / 2) + int(self.WIDTH * 0.01)
        self.top_position = 20

        self.environment_overview_text = dpg.generate_uuid()
        self.agent_overview_text = dpg.generate_uuid()
        self.agent_information_text = dpg.generate_uuid()
        self.agent_information_table = {}
        self.agent_interaction_table = {}

    def draw_interaction(self, source_agent, target_agent, color, tag: str = None):
        if tag is None:
            dpg.draw_line((source_agent.x_pos, source_agent.y_pos), (target_agent.x_pos, target_agent.y_pos), color=color_dict[color])
        else:
            dpg.draw_line((source_agent.x_pos, source_agent.y_pos), (target_agent.x_pos, target_agent.y_pos),
                                 color=color_dict[color], tag=tag)

    def update_agent_overview(self):
        dpg.set_value(self.agent_overview_text, f"current episode: {self.environment.current_step}")
        for agent in self.environment.agents:
            agent_str = f"capital: {agent.capital}\ninventory: {agent.inventory}"
            dpg.set_value(self.agent_information_table[agent.name], agent_str)
            random_agent = random.choice(self.environment.agents)
            if random_agent != agent:
                pass
                #self.draw_interaction(agent, random_agent, "red")

    def step(self):
        dpg.set_value(self.environment_overview_text, f"current episode: {self.environment.current_episode} \nmax episodes: {self.environment.max_episodes}\ncurrent step: {self.environment.current_step} \nmax steps {self.environment.max_steps}")
        self.update_agent_overview()

        dpg.render_dearpygui_frame()

    def is_running(self):
        return dpg.is_dearpygui_running()

    def draw_world(self):
        num_agents = len(self.environment.agents)
        radius = 150
        with dpg.drawlist(width=self.agent_world_width, height=self.agent_world_height):
            for idx, agent in enumerate(self.environment.agents):
                angle = math.pi * 2 * idx / num_agents
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                agent.x_pos = x + self.agent_world_middle_position[0]
                agent.y_pos = y + self.agent_world_middle_position[1]
                dpg.draw_circle((agent.x_pos, agent.y_pos), 10, color=[0, 255, 0], fill=[0, 255, 0])
                for target_idx, target_agent in enumerate(self.environment.agents):
                    if target_idx == idx:
                        continue
                    else:
                        self.draw_interaction(self.environment.agents[idx], self.environment.agents[target_idx], "gray", tag=f"{agent}_{target_agent}")

    def add_menu_bar(self):
        with dpg.viewport_menu_bar(indent=4):
            with dpg.menu(label="Tabs"):
                dpg.add_menu_item(label="Market", callback=print_me)
                dpg.add_menu_item(label="Environment", callback=print_me)

    def draw_environment_overview(self):
        with dpg.collapsing_header(label="Environment Overview", default_open=True):
            self.environment_overview_text = dpg.add_text("", wrap=300)

    def draw_agent_overview(self):
        with dpg.collapsing_header(label="Agent Overview", default_open=True):
            self.agent_overview_text = dpg.add_text("", wrap=300)

    def add_agent_information_table(self):
        with dpg.collapsing_header(label="Agent information", default_open=True):
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

    def create_environment_info_window(self):
        with dpg.window(label="Information", tag="Info", width=self.info_tab_width, height=self.info_tab_height, pos=(self.agent_world_width, 0), no_close=True, no_move=True, no_scrollbar=True, no_collapse=True, autosize=True, no_resize=True):
            self.draw_environment_overview()
            self.draw_agent_overview()
            self.add_agent_information_table()

    def create_world_window(self):
        with dpg.window(label="Agent World", tag="World", width=self.agent_world_width, height=self.agent_world_height, no_close=True, no_move=True, no_scrollbar=True, no_collapse=True, autosize=True, no_resize=True):
            dpg.add_spacer(height=self.top_position)
            self.draw_world()

    def reset(self, environment):
        self.environment = environment

    def __enter__(self):
        dpg.create_context()
        self.create_world_window()
        self.create_environment_info_window()

        with dpg.handler_registry():
            pass
            #dpg.add_mouse_move_handler(callback=self.update_plot_data, user_data=self.plot_data)

        dpg.create_viewport(title='Complex Adaptive Economic Simulator', width=self.WIDTH, height=self.HEIGHT)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        self.add_menu_bar()

        #dpg.set_primary_window("Example Window", True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        dpg.destroy_context()



