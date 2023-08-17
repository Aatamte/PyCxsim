import dearpygui.dearpygui as dpg


class BottomPanel:
    def __init__(self, visualizer, environment, HEIGHT, WIDTH):
        self.visualizer = visualizer
        self.environment = environment
        self.HEIGHT = int(HEIGHT * 0.2)
        self.WIDTH = int(2 * WIDTH / 3)
        self.pos_y = int(HEIGHT * 0.8)
        self.bottom = None

        self.pause_button = None
        self.play_button = None

    def pause_simulation_callback(self, sender):
        self.visualizer.is_paused = True

    def resume_simulation_callback(self, sender):
        self.visualizer.is_paused = False

    def update(self):
        self.HEIGHT = int(dpg.get_viewport_height() * 0.2)
        self.WIDTH = int(2 * dpg.get_viewport_width() / 3)
        self.pos_y = int(dpg.get_viewport_height() * 0.8)
        dpg.set_item_width(self.bottom, self.WIDTH)
        dpg.set_item_height(self.bottom, self.HEIGHT)
        dpg.set_item_pos(self.bottom, [0, self.pos_y])

    def create(self):
        with dpg.window(
            label="Bottom Panel", tag="Bottom",
            width=self.WIDTH,
            height=self.HEIGHT,
            no_close=True,
            no_move=True,
            menubar=False,
            no_scrollbar=True,
            no_collapse=True,
            no_resize=True,
            no_title_bar=True,
            pos=(0, self.pos_y)
        ) as self.bottom:
            self.pause_button = dpg.add_button(label="Pause", pos=(0, int(self.HEIGHT / 4)), callback=self.pause_simulation_callback, height=int(self.HEIGHT / 2), width=int(self.HEIGHT / 2))
            self.play_button = dpg.add_button(label="Resume", pos=(int(self.HEIGHT / 2), int(self.HEIGHT / 4)), callback=self.resume_simulation_callback, height=int(self.HEIGHT / 2), width=int(self.HEIGHT / 2))


