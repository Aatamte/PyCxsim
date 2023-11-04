# standard visuals
from cxsim.gui.std_visuals.worldview import MainView
from cxsim.gui.std_visuals.top_panel import TopPanel
from cxsim.gui.std_visuals.sidebar_window import Sidebar

# utilities
from cxsim.utilities.background_jobs.job_manager import JobManager
from cxsim.gui.assets.path_definition import ASSET_PATH

import time
import dearpygui.dearpygui as dpg

dpg.create_context()

MAIN_VIEW_HEIGHT_FACTOR = 0.9
MAIN_VIEW_WIDTH_FACTOR = 0.6666
SIDEBAR_WIDTH_FACTOR = 0.33333
SIDEBAR_X_POSITION_FACTOR = 3 / 5


class DimensionConfig:
    def __init__(self, total_width=1400, total_height=1000):
        self.total_width = total_width
        self.total_height = total_height
        self.positions = {
            'sidebar': (0, 0),  # Initialized to default positions; these can be updated as needed
            'main_view': (0, 0),
            'top_panel': (0, 0)
        }

    @property
    def main_view_height(self):
        return int(self.total_height * MAIN_VIEW_HEIGHT_FACTOR)

    @property
    def main_view_width(self):
        return int(self.total_width * MAIN_VIEW_WIDTH_FACTOR)

    @property
    def sidebar_height(self):
        return self.total_height

    @property
    def sidebar_width(self):
        return int(self.total_width * SIDEBAR_WIDTH_FACTOR)

    @property
    def top_panel_height(self):
        return int(self.total_height * int(1 - MAIN_VIEW_HEIGHT_FACTOR))

    @property
    def top_panel_width(self):
        return int(self.total_width * MAIN_VIEW_WIDTH_FACTOR)

    def update_dimensions(self, total_width, total_height):
        self.total_width = total_width
        self.total_height = total_height

    def update_positions(self, element_name, x, y):
        self.positions[element_name] = (x, y)

    def get_position(self, element_name):
        return self.positions.get(element_name, (0, 0))  # Default to (0, 0) if the element name is not found


class GUI:
    def __init__(self, close_on_finish: bool = False):
        self.environment = None
        self.close_on_finish = close_on_finish
        self.dimension_config = DimensionConfig()

        self.last_environment_step = 0

        self.is_paused = True
        self.skip_steps = 0

        # main three components of the GUI
        self.main_view = None
        self.top_panel = None
        self.sidebar = None

        self.job_manager = JobManager()
        self.background_tasks_exist = False

    def step(self, is_new_step):
        self.main_view.render()
        self.top_panel.render()
        self.sidebar.render()

        dpg.render_dearpygui_frame()

    def compile(self, environment):
        self.environment = environment

        self.main_view = MainView(environment, self.dimension_config)
        self.main_view.blocks = environment.starting_block_size

        self.top_panel = TopPanel(self, environment, self.dimension_config)

        self.sidebar = Sidebar(environment, self.dimension_config)

    def reset(self, environment):
        self.environment = environment
        if "Gridworld" in self.environment.artifact_lookup.keys():
            print(self.environment.artifact_lookup["Gridworld"].x_size)
            self.main_view.blocks = self.environment.artifact_lookup["Gridworld"].x_size

        self.start()

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
        self.dimension_config.update_dimensions(
            dpg.get_viewport_width(),
            dpg.get_viewport_height()
        )

        self.sidebar.resize()
        self.main_view.resize()
        self.top_panel.resize()

    def start(self):
        self.top_panel.create()
        self.main_view.create()
        self.sidebar.create()

        with dpg.theme():
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (200, 200, 100), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)

        dpg.set_viewport_resize_callback(self.resize)

        dpg.create_viewport(
            title='PyCxsim',
            width=self.dimension_config.total_width,
            height=self.dimension_config.total_height,
            small_icon=ASSET_PATH.joinpath("large_icon.ico").__str__(),
            large_icon=ASSET_PATH.joinpath("large_icon.ico").__str__()
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_viewport_vsync(True)

    @staticmethod
    def close():
        dpg.stop_dearpygui()
        dpg.destroy_context()

    def __del__(self):
        dpg.destroy_context()



