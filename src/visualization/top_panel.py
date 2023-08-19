import dearpygui.dearpygui as dpg


class TopPanel:
    def __init__(self, visualizer, environment, HEIGHT, WIDTH):
        self.visualizer = visualizer
        self.environment = environment
        self.HEIGHT = int(HEIGHT * 0.05)
        self.WIDTH = int(2 * WIDTH / 3)
        self.pos_y = 0
        self.panel = None

        self.pause_button = None
        self.play_button = None

        self.play_pause_button_sizes = {"height": 50, "width": 50}

        self.current_status_dpg_uuid = dpg.generate_uuid()
        self.current_status = True

    def pause_simulation_callback(self, sender):
        self.visualizer.is_paused = True

    def resume_simulation_callback(self, sender):
        self.visualizer.is_paused = False

    def update(self):
        pass

    def resize(self):
        self.HEIGHT = int(dpg.get_viewport_height() * 0.1)
        self.WIDTH = int(2 * dpg.get_viewport_width() / 3)

        dpg.set_item_height(self.panel, self.HEIGHT)    # doesnt seem to work right????
        dpg.set_item_width(self.panel, self.WIDTH)

    def create(self):
        with dpg.window(
            label="Top Panel",
            tag="panel",
            pos=(0, 0),
            height=self.HEIGHT,
            width=self.WIDTH,
            no_close=True,
            no_move=True,
            menubar=False,
            no_scrollbar=True,
            no_collapse=True,
            no_resize=True,
            no_title_bar=True,
        ) as self.panel:

            self.current_status_dpg_uuid = dpg.add_text(str(self.visualizer.is_paused))

            self.pause_button = dpg.add_button(
                label="Pause",
                pos=(0, int(self.HEIGHT / 4)),
                callback=self.pause_simulation_callback,
                height=self.play_pause_button_sizes["height"],
                width=self.play_pause_button_sizes["width"]
            )

            self.play_button = dpg.add_button(
                label="Resume",
                pos=(int(self.play_pause_button_sizes["width"] * 1.5), int(self.HEIGHT / 4)),
                callback=self.resume_simulation_callback,
                height=self.play_pause_button_sizes["height"],
                width=self.play_pause_button_sizes["width"]
            )


