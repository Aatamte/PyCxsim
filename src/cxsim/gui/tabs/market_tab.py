from src.cxsim.gui.tabs.tab import Tab
import dearpygui.dearpygui as dpg


class MarketplaceTab(Tab):
    def __init__(self):
        super(MarketplaceTab, self).__init__("Marketplace", "market_tab")
        self.environment = None
        self.marketplace = None

        self.current_market = None
        self.window = None

        self.current_market_info = None
        self.market_history = dpg.generate_uuid()
        self.text = None

        self.best_bid_plot = []
        self.best_ask_plot = []

    def step(self):
        longest_series = max(len(self.best_bid_plot), len(self.best_ask_plot))

        # Calculate the x-offsets for each series
        x_offset_bid = longest_series - len(self.best_bid_plot)
        x_offset_ask = longest_series - len(self.best_ask_plot)

        # Generate the x-coordinates for each series
        x_coords_bid = [n + x_offset_bid for n in range(len(self.best_bid_plot))]
        x_coords_ask = [n + x_offset_ask for n in range(len(self.best_ask_plot))]

        dpg.set_value(self.best_bid, [x_coords_bid, self.best_bid_plot])
        dpg.set_value(self.best_ask, [x_coords_ask, self.best_ask_plot])
        dpg.set_value(self.text, self.marketplace[self.current_market])
        dpg.set_value(self.market_history, self.marketplace[self.current_market].history)

    def get_window(self):
        return self.window

    def show(self):
        dpg.show_item(self.window)

    def show_good_plot_callback(self, sender, data):
        self.current_market = data
        self.best_bid_plot = self.marketplace[data].best_bid_history
        self.best_ask_plot = self.marketplace[data].best_ask_history
        #self.text = self.marketplace[data]

    def draw(self):
        self.current_market = list(self.marketplace.markets.keys())[0]
        self.best_bid_plot = self.marketplace[self.current_market].best_bid_history
        self.best_ask_plot = self.marketplace[self.current_market].best_ask_history

        with dpg.child_window(label=self.name, show=False) as self.window:
            dpg.add_combo(label="good", items=[good for good in list(self.marketplace.markets.keys())], callback=self.show_good_plot_callback)
            with dpg.plot(label=f"Market for {self.current_market}", height=400, width=400):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="step", tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="price", tag="y_axis")
                dpg.set_axis_limits_auto("y_axis")

                self.best_bid = dpg.add_line_series(
                    [n for n in range(len(self.best_bid_plot))],
                    self.best_bid_plot,
                    label="best bid",
                    parent="y_axis",

                )

                self.best_ask = dpg.add_line_series(
                    [n for n in range(len(self.best_ask_plot))],
                    self.best_ask_plot,
                    label="best ask",
                    parent="y_axis",
                )

            self.text = dpg.add_text("", wrap=300)

            self.market_history = dpg.add_text("", wrap=450)

    def reset(self, env):
        self.environment = env
        if "Marketplace" in self.environment.action_handler.artifacts.keys():
            self.marketplace = self.environment.action_handler.artifacts["Marketplace"]

