import dearpygui.dearpygui as dpg
from cxsim.gui.std_visuals.logs_popup_window import LogsWindow
from cxsim.gui.std_visuals.agent_overview import AgentOverview
from cxsim.gui.std_tabs.marketplace_tab import MarketplaceTab

TAB_registry = {
    "Marketplace": MarketplaceTab
}


class Sidebar:
    def __init__(self, environment, dimension_config):
        self.environment = environment
        self.dimension_config = dimension_config
        self.agent_overview = AgentOverview(environment=self.environment)
        self.log_window = LogsWindow(environment=environment)

        self.artifact_names = []
        self.tabs = {

        }

        self.header_windows = {
            "agent_overview": self.agent_overview,
            "log_window": self.log_window
        }

        self.current_tab = None

    def add_tab(self, name: str, item):
        self.tabs[name] = item

    def render(self):
        for name, tab in self.tabs.items():
            tab.step()

    def resize(self):
        # Update the dimensions of the sidebar
        sidebar_width = self.dimension_config.sidebar_width
        sidebar_height = self.dimension_config.sidebar_height
        dpg.set_item_width(self.sidebar, sidebar_width)
        dpg.set_item_height(self.sidebar, sidebar_height)

        dpg.set_item_pos(self.sidebar, (self.dimension_config.main_view_width, 0))

    def create(self):
        for artifact_name in self.environment.artifact_lookup.keys():
            if artifact_name in TAB_registry.keys():
                self.tabs[artifact_name] = TAB_registry[artifact_name](self.environment, self.environment.artifact_lookup[artifact_name])

        with dpg.window(
                label="Information", tag="Info",
                height=self.dimension_config.sidebar_height,
                width=self.dimension_config.sidebar_width,
                pos=(self.dimension_config.sidebar_width, 0),
                no_close=True, no_move=True,
                no_scrollbar=True,
                no_collapse=True,
                no_resize=True,
                no_title_bar=True
        ) as self.sidebar:
            with dpg.menu_bar(label="Information menu bar"):
                with dpg.menu(label="Environment"):
                    dpg.add_menu_item(label="Overview", tag="show_overview", callback=self._show_callback)
                    dpg.add_menu_item(label="Actions", tag="show_actions", callback=self._show_callback)

                dpg.add_menu_item(label="Agents", tag="agent_overview", callback=self._show_callback)

                with dpg.menu(label="Artifacts"):
                    for artifact_name in self.tabs.keys():
                        dpg.add_menu_item(label=artifact_name, tag=artifact_name, callback=self._show_callback)

                dpg.add_menu_item(label="Settings")

                dpg.add_menu_item(label="Logs", tag="log_window", callback=self._show_callback)

            self.agent_overview.draw()
            self.log_window.draw()

            for artifact_name, artifact_tab in self.tabs.items():
                artifact_tab.draw()

    def _show_callback(self, sender):
        if sender == "log_window":
            self.header_windows[sender].set_show(False)
            self.header_windows[sender].set_show(True)

        # Hide the current tab
        if self.current_tab and self.current_tab != "log_window":
            if self.current_tab in self.tabs:
                self.tabs[self.current_tab].set_show(False)
            elif self.current_tab in self.header_windows:
                self.header_windows[self.current_tab].set_show(False)

        # Show the sender tab
        if sender in self.tabs:
            self.tabs[sender].set_show(True)
            self.current_tab = sender
        elif sender in self.header_windows:
            self.header_windows[sender].set_show(True)
            self.current_tab = sender


