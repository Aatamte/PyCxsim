import dearpygui.dearpygui as dpg
import math
import numpy as np
import random

# Dictionary of 50 different colors and their RGBA values
colors = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'pink': (255, 105, 180),
    'brown': (139, 69, 19),
    'gray': (128, 128, 128),
    'lime': (0, 255, 0),
    'violet': (238, 130, 238),
    'indigo': (75, 0, 130),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    'beige': (245, 245, 220),
    'gold': (255, 215, 0),
    'teal': (0, 128, 128),
    'coral': (255, 127, 80),
    'aqua': (0, 255, 255),
    'navy': (0, 0, 128),
    'silver': (192, 192, 192),
    'olive': (128, 128, 0),
    'maroon': (128, 0, 0),
    'turquoise': (64, 224, 208),
    'khaki': (240, 230, 140),
    'lavender': (230, 230, 250),
    'plum': (221, 160, 221),
    'tan': (210, 180, 140),
    'azure': (240, 255, 255),
    'mint': (189, 252, 201),
    'chocolate': (210, 105, 30),
    'ivory': (255, 255, 240),
    'sandy': (210, 180, 140),
    'wheat': (245, 222, 179),
    'bisque': (255, 228, 196),
    'goldenrod': (218, 165, 32),
    'firebrick': (178, 34, 34),
    'salmon': (250, 128, 114),
    'darkgreen': (0, 100, 0),
    'skyblue': (135, 206, 235),
    'darkorchid': (153, 50, 204),
    'darkslategray': (47, 79, 79),
    'mediumvioletred': (199, 21, 133),
    'mediumturquoise': (72, 209, 204),
    'mediumspringgreen': (0, 250, 154),
    'mediumslateblue': (123, 104, 238),
    'mediumseagreen': (60, 179, 113),
    'mediumblue': (0, 0, 205),
    'mediumaquamarine': (102, 205, 170),
    'darkviolet': (148, 0, 211),
}
# Ensure that we have exactly 50 colors
assert len(colors) == 50

# List to keep track of used colors
used_colors = []


def get_random_unused_color():
    # Get all unused colors
    unused_colors = [color for color in colors.keys() if color not in used_colors]

    # If all colors have been used, return None
    if not unused_colors:
        return None

    # Randomly choose an unused color
    chosen_color_name = random.choice(unused_colors)
    chosen_color_value = colors[chosen_color_name]

    # Mark the color as used
    used_colors.append(chosen_color_name)

    return chosen_color_name, chosen_color_value


class World:
    def __init__(self, environment, starting_WIDTH, starting_HEIGHT):
        self.HEIGHT = int(starting_HEIGHT * 0.95)
        self.WIDTH = int(3 * starting_WIDTH / 5)
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

    def update(self):
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
        self.HEIGHT = int(dpg.get_viewport_height() * 0.95)
        self.WIDTH = int(3 * dpg.get_viewport_width() / 5)
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
        if self.blocks is None:
            self.blocks = 10
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
