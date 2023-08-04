from src.new_visualization.tabs.tab import Tab
import dearpygui.dearpygui as dpg


class MarketTab(Tab):
    def __init__(self):
        super(MarketTab, self).__init__("Market", "market_tab")
        self.environment = None
        self.market = None
        self.best_bid_plot = []
        self.best_ask_plot = []

    def step(self):
        self.best_bid_plot.append(self.market.market.highest_bid_order.price)
        dpg.set_value(self.best_bid, [[n for n in range(len(self.best_bid_plot))], self.best_bid_plot])
        self.best_ask_plot.append(self.market.market.lowest_offer_order.price)
        dpg.set_value(self.best_ask, [[n for n in range(len(self.best_ask_plot))], self.best_ask_plot])
        dpg.fit_axis_data("y_axis")
        dpg.fit_axis_data("x_axis")
        dpg.set_value(self.text, str(self.market))

    def get_window(self):
        return self.window

    def show(self):
        dpg.show_item(self.window)

    def draw(self):
        with dpg.child_window(label=self.name, show=False) as self.window:
            with dpg.plot(label=f"Market for {self.market.market_name}", height=400, width=400):
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
        self.market = self.environment.artifact_controller.artifacts["Market"]

