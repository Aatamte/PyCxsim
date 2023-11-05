from cxsim.gui.tab import Tab
import dearpygui.dearpygui as dpg
from cxsim.gui.utils.plots import Plot


class MarketplaceTab(Tab):
    def __init__(self, environment, artifact):
        super(MarketplaceTab, self).__init__("Marketplace", "market_tab", environment, artifact)
        self.marketplace = self.artifact
        self.current_market = None
        self.window = None

        self.current_market_info = None
        self.market_history = dpg.generate_uuid()
        self.text = None

    def step(self):
        # Assuming market_plot is the instance of the Plot class
        self.market_plot.update_series("best_bid",  self.marketplace[self.current_market].best_bid_history)
        self.market_plot.update_series("best_ask", self.marketplace[self.current_market].best_ask_history)

        dpg.set_value(self.text, self.marketplace[self.current_market])

    def get_window(self):
        return self.window

    def show(self):
        dpg.show_item(self.window)

    def show_good_plot_callback(self, sender, data):
        self.current_market = data

    def draw(self):
        self.current_market = list(self.marketplace.markets.keys())[0]

        with dpg.child_window(label=self.name, show=False) as self.window:
            dpg.add_combo(label="good", items=[good for good in list(self.marketplace.markets.keys())], callback=self.show_good_plot_callback)

            self.market_plot = Plot(parent=self.window, label=f"Market for {self.current_market}", height=400, width=400, series_names=["best_bid", "best_ask"])

            self.market_plot.create_plot()

            self.text = dpg.add_text("", wrap=300)

            self.market_history = dpg.add_text("", wrap=450)

    def reset(self, env):
        self.environment = env
        if "Marketplace" in self.environment.action_handler.artifacts.keys():
            self.marketplace = self.environment.action_handler.artifacts["Marketplace"]

