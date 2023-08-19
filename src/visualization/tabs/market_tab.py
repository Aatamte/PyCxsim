from src.visualization.tabs.tab import Tab
import dearpygui.dearpygui as dpg


class MarketplaceTab(Tab):
    def __init__(self):
        super(MarketplaceTab, self).__init__("Marketplace", "market_tab")
        self.environment = None
        self.marketplace = None

        self.current_market = None
        self.window = None

        self.best_bid_plot = []
        self.best_ask_plot = []

    def step(self):
        dpg.set_value(self.best_bid, [[n for n in range(len(self.best_bid_plot))], self.best_bid_plot])
        dpg.set_value(self.best_ask, [[n for n in range(len(self.best_ask_plot))], self.best_ask_plot])
        dpg.fit_axis_data("y_axis")
        dpg.fit_axis_data("x_axis")
        dpg.set_value(self.text, str("hello"))

    def get_window(self):
        return self.window

    def show(self):
        dpg.show_item(self.window)

    def show_good_plot_callback(self, sender, data):
        print(sender, data)
        self.current_market = data
        self.best_bid_plot = self.marketplace[data].best_bid_history
        self.best_ask_plot = self.marketplace[data].best_ask_history

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

    def reset(self, env):
        self.environment = env
        self.marketplace = self.environment.artifact_controller.artifacts["Marketplace"]

