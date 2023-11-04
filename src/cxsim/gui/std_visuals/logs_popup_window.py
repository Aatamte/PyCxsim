import dearpygui.dearpygui as dpg
import logging


class LogsWindow(logging.Handler):
    def __init__(self, environment):
        super().__init__()
        self.show = False
        self.environment = environment
        self.window = None
        self.log_widget = None
        self.early_logs = []  # Queue for logs before GUI is initialized
        # Set the detailed formatter directly inside the handler
        detailed_format = ("[%(asctime)s] [%(name)s] [%(levelname)s] "
                           "[%(filename)s:%(lineno)d in %(funcName)s] - %(message)s")
        formatter = logging.Formatter(detailed_format)
        self.setFormatter(formatter)
        self.environment.logger.addHandler(self)

    def get_color(self, level):
        color_map = {
            logging.DEBUG: (0, 0, 255),       # Blue
            logging.INFO: (0, 255, 0),       # Green
            logging.WARNING: (255, 255, 0),  # Yellow
            logging.ERROR: (255, 0, 0),      # Red
            logging.CRITICAL: (128, 0, 128)  # Purple
        }
        return color_map.get(level, (0, 0, 0))  # Default to black

    def emit(self, record):
        # If the window hasn't been initialized, queue the log
        if self.window is None:
            self.early_logs.append(record)
            return
        # Format the record using the set formatter
        msg = self.format(record)
        color = self.get_color(record.levelno)

        # Generate a unique ID for the new text widget
        unique_id = dpg.generate_uuid()

        # Add the new text widget with the unique ID to the window
        dpg.add_text(msg, color=color, parent=self.window, id=unique_id, wrap=500)

    def display_early_logs(self):
        # Display queued logs after GUI initialization
        for record in self.early_logs:
            self.emit(record)
        self.early_logs.clear()  # Clear the queue after processing

    def update(self):
        pass

    def get_window(self):
        return self.window

    def draw(self):
        with dpg.window(label="Logs", show=self.show, width=550, height=800) as self.window:
            self.display_early_logs()

    def set_show(self, value: bool):
        print(value)
        self.show = value
        if value:
            dpg.show_item(self.window)
        else:
            dpg.hide_item(self.window)
