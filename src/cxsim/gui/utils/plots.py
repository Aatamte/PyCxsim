import dearpygui.dearpygui as dpg


class Plot:
    def __init__(self, parent, label, height, width, series_names):
        self.parent = parent
        self.label = label
        self.height = height
        self.width = width
        self.series_names = series_names
        self.plot_id = None
        self.y_axis_id = None
        self.x_axis_id = None

        self.series = {}

    def create_plot(self):
        with dpg.plot(label=self.label, height=self.height, width=self.width, parent=self.parent) as self.plot_id:
            dpg.add_plot_legend()
            self.x_axis_id = dpg.add_plot_axis(dpg.mvXAxis, label="step", tag="x_axis")
            self.y_axis_id = dpg.add_plot_axis(dpg.mvYAxis, label="price", tag="y_axis")

            # Create line series based on provided series names
            for name in self.series_names:
                self.series[name] = dpg.add_line_series([], [], label=name, parent="y_axis")

    def update_series(self, name, y_data, label=None):
        # Use aligned_x_coordinates to get the x-coordinates
        aligned_coords = self.aligned_x_coordinates(**{name: y_data})
        x_data = aligned_coords[name]

        if name not in self.series:
            self.series[name] = dpg.add_line_series(x_data, y_data, label=label if label else name,
                                                    y_axis=self.y_axis_id)
        else:
            dpg.set_value(self.series[name], [x_data, y_data])

    def aligned_x_coordinates(self, **series_data):
        """
        Returns aligned x-coordinates for multiple series so that their latest values align on the x-axis.

        Parameters:
        - series_data: Dictionary where key is the series name and value is the data for that series.

        Returns:
        - Dictionary with aligned x-coordinates for each series.
        """
        # Determine the longest series length
        longest_series = max(len(data) for data in series_data.values())

        aligned_coords = {}
        for name, data in series_data.items():
            # Calculate the offset for the current series
            x_offset = longest_series - len(data)

            # Update the x-coordinates based on the offset
            x_coords = [n + x_offset for n in range(len(data))]

            aligned_coords[name] = x_coords

        return aligned_coords

    def get_plot_id(self):
        return self.plot_id
