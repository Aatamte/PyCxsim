from cxsim.gui.assets.utils import COLORS

import dearpygui.dearpygui as dpg
import numpy as np
import random

# List to keep track of used COLORS
used_COLORS = []


def get_random_unused_color():
    # Get all unused COLORS
    unused_COLORS = [color for color in COLORS.keys() if color not in used_COLORS]

    # If all COLORS have been used, return None
    if not unused_COLORS:
        unused_COLORS = [color for color in COLORS.keys()]

    # Randomly choose an unused color
    chosen_color_name = random.choice(unused_COLORS)
    chosen_color_value = COLORS[chosen_color_name]

    # Mark the color as used
    used_COLORS.append(chosen_color_name)

    return chosen_color_name, chosen_color_value


class MainView:
    def __init__(self, environment, dimension_config):
        self.dimension_config = dimension_config
        self.HEIGHT = dimension_config.main_view_height
        self.WIDTH = dimension_config.main_view_width
        self.world = None
        self.grid = None
        self.environment = environment
        self.blocks = None

        self.agent_circles = {}
        self.agent_names = {}

        self.agent_positions = None

        self.tiles = None

        self.block_size_x = None
        self.block_size_y = None

    def get_middle_of_block(self, block_x, block_y, block_size_x, block_size_y):
        middle_x = block_x * block_size_x + block_size_x / 2
        # Invert the y-coordinate
        middle_y = ((self.blocks - (block_y + 1)) * block_size_y + block_size_y / 2)
        return middle_x, middle_y

    def choose_and_set_position(self):
        # Find the positions of the zero entries
        zero_positions = np.argwhere(self.agent_positions == 0)

        # If there are no zero entries, return None
        if zero_positions.size == 0:
            return None

        # Randomly choose one of the zero positions
        chosen_position = zero_positions[np.random.choice(zero_positions.shape[0])]

        # Set that position to 1
        self.agent_positions[tuple(chosen_position)] = 1

        return tuple(chosen_position)

    def render(self):
        for idx, agent in enumerate(self.environment.agents):
            x = agent.x_pos
            y = agent.y_pos
            x, y = self.get_middle_of_block(x, y, self.block_size_x, self.block_size_y)

            dpg.delete_item(self.agent_circles[agent.name])
            dpg.delete_item(self.agent_names[agent.name])

            self.agent_circles[agent.name] = dpg.draw_circle(
                (x, y),
                int(self.block_size_y // 2),
                color=[0, 0, 0],
                fill=list(agent.color),
                parent=self.grid
            )

            text_size = int(self.block_size_x * 0.2)

            self.agent_names[agent.name] = dpg.draw_text(
                text=agent.name,
                pos=(int(x - (self.block_size_x / 3)), int(y - (self.block_size_x / 10))),
                color=[0, 0, 0],
                size=text_size,
                parent=self.grid
            )

    def reset(self, n_blocks: int = None):
        pass

    def resize(self):
        self.HEIGHT = self.dimension_config.main_view_height
        self.WIDTH = self.dimension_config.main_view_width
        dpg.set_item_width(self.world, self.WIDTH)
        dpg.set_item_height(self.world, self.HEIGHT)
        dpg.delete_item(self.grid)
        if self.HEIGHT < self.WIDTH:
            scale_factor = self.HEIGHT
        else:
            scale_factor = self.WIDTH

        self.block_size_x = int(0.9 * scale_factor) / self.blocks
        self.block_size_y = int(0.9 * scale_factor) / self.blocks

        with dpg.drawlist(
                width=self.WIDTH,
                height=int(self.HEIGHT * 0.95),
                parent=self.world,

        ) as self.grid:
            self.draw_background(True)
            self.place_agents(True)

    def draw_background(self, resize: bool = False):
        for row in range(self.blocks):
            for col in range(self.blocks):
                x1 = col * self.block_size_x
                y1 = row * self.block_size_y
                x2 = x1 + self.block_size_x
                y2 = y1 + self.block_size_y

                self.tiles[row][col] = dpg.draw_quad(
                    p1=(x1, y1),
                    p2=(x2, y1),
                    p3=(x2, y2),
                    p4=(x1, y2),
                    color=(0, 0, 0, 255),
                    fill=(211, 211, 211, 255)
                )

    def place_agents(self, resize: bool = False):
        for idx, agent in enumerate(self.environment.agents):
            if agent.x_pos is None and agent.y_pos is None:
                x, y = self.choose_and_set_position()
                agent.x_pos = x
                agent.y_pos = y
            x = agent.x_pos
            y = agent.y_pos
            x, y = self.get_middle_of_block(x, y, self.block_size_x, self.block_size_y)

            if agent.color == (0, 0, 0):
                name, color = get_random_unused_color()
                agent.color = color

            self.agent_circles[agent.name] = dpg.draw_circle(
                (x, y),
                int(self.block_size_y // 2),
                color=[0, 0, 0],
                fill=list(agent.color)
            )

            text_size = int(self.block_size_x * 0.2)

            agent_name_length = len(agent.name)

            self.agent_names[agent.name] = dpg.draw_text(
                text=agent.name,
                pos=(int(x - (self.block_size_x / 3)), int(y - (self.block_size_x / 10))),
                color=[0, 0, 0],
                size=text_size
            )

    def set_up(self):
        with dpg.drawlist(
                width=self.WIDTH,
                height=self.HEIGHT,
                parent=self.world,
        ) as self.grid:
            self.draw_background()
            self.place_agents()

    def create(self):
        self.agent_positions = np.zeros((self.blocks, self.blocks))

        self.tiles = [[dpg.generate_uuid() for _ in range(self.blocks)] for _ in range(self.blocks)]

        self.block_size_x = int(0.5 * self.WIDTH) / self.blocks
        self.block_size_y = int(0.5 * self.HEIGHT) / self.blocks
        with dpg.window(
            label="Environment",
            tag="World",
            pos=(0, int(self.HEIGHT * 0.1)),
            height=self.HEIGHT,
            width=self.WIDTH,
            no_close=True,
            no_move=True,
            menubar=False,
            no_scrollbar=False,
            no_collapse=True,
            no_resize=True,
            no_title_bar=True,
        ) as self.world:
            self.set_up()

    def draw(self):
        pass
