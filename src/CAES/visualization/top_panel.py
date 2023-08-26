import dearpygui.dearpygui as dpg


class TopPanel:
    def __init__(self, visualizer, environment, HEIGHT, WIDTH):
        self.visualizer = visualizer
        self.environment = environment
        self.HEIGHT = int(HEIGHT * 0.1)
        self.WIDTH = int(3 * WIDTH / 5)
        self.pos_y = 0
        self.panel = None

        self.pause_button = None
        self.play_button = None

        self.text_size = 10

        self.play_pause_button_sizes = {"height": 50, "width": 50}

        self.current_status_dpg_uuid = dpg.generate_uuid()

        self.environment_name_text_uuid = dpg.generate_uuid()

        self.current_step_uuid = dpg.generate_uuid()

        self.n_agents_text_uuid = dpg.generate_uuid()

        self.n_artifacts_text_uuid = dpg.generate_uuid()

        self.next_step = dpg.generate_uuid()

    def pause_simulation_callback(self, sender):
        self.visualizer.is_paused = True

    def resume_simulation_callback(self, sender):
        self.visualizer.is_paused = False

    def skip_simulation_callback(self, sender):
        self.visualizer.skip_steps = 1
        #self.visualizer.is_paused = True

    def update(self):
        dpg.set_value(self.current_step_uuid, f"Current step: {self.environment.current_step} / {self.environment.max_steps}")

    def resize(self):
        self.HEIGHT = int(dpg.get_viewport_height() * 0.1)
        self.WIDTH = int(3 * dpg.get_viewport_width() / 5)

        dpg.set_item_height(self.panel, self.HEIGHT)    # doesnt seem to work the correct way
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

            self.pause_button = dpg.add_button(
                label="Pause",
                pos=(400, int(self.HEIGHT / 4)),
                callback=self.pause_simulation_callback,
                height=self.play_pause_button_sizes["height"],
                width=self.play_pause_button_sizes["width"]
            )

            self.play_button = dpg.add_button(
                label="Resume",
                pos=(455, int(self.HEIGHT / 4)),
                callback=self.resume_simulation_callback,
                height=self.play_pause_button_sizes["height"],
                width=self.play_pause_button_sizes["width"]
            )

            self.next_step = dpg.add_button(
                label="Skip",
                pos=(510, int(self.HEIGHT / 4)),
                callback=self.skip_simulation_callback,
                height=self.play_pause_button_sizes["height"],
                width=self.play_pause_button_sizes["width"]
            )

            self.environment_name_text_uuid = dpg.add_text(f"Environment name: {self.environment.name}")
            self.current_step_uuid = dpg.add_text(f"Current step: {self.environment.current_step} / {self.environment.max_steps}")
            self.n_agents_text_uuid = dpg.add_text(f"Number of Agents: {self.environment.n_agents}")
            self.n_artifacts_text_uuid = dpg.add_text(f"Number of Artifacts: {self.environment.n_artifacts}")
