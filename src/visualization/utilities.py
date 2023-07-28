import pandas as pd
import pygame
import math


class Tab:
    def __init__(self, parent_visualizer):
        self.parent_visualizer = parent_visualizer
        self.background_color = "black"
        self.color_dict = {
                'red': (255, 0, 0),
                'green': (0, 255, 0),
                'blue': (0, 0, 255),
                'yellow': (255, 255, 0),
                'orange': (255, 165, 0),
                'purple': (128, 0, 128),
                'pink': (255, 192, 203),
                'brown': (165, 42, 42),
                'gray': (128, 128, 128),
                'black': (0, 0, 0),
                'white': (255, 255, 255),
        }
        self._top_position = 60
        self._left_side_position = (self.parent_visualizer.SCREEN_WIDTH / 2) + 5
        self.background_color = self.background_color.lower()

    def write_text(self, text: str, font_size: int = 20, color: str = "black"):
        self._left_side_position = (self.parent_visualizer.SCREEN_WIDTH / 2) + 5
        self._is_valid_color(color)
        self.parent_visualizer.display.blit(
            pygame.font.Font(None, font_size).render(text, True, color),
            (self._left_side_position, self._top_position)
        )

    def write_dataframe(self, df: pd.DataFrame):
        self._left_side_position = (self.parent_visualizer.SCREEN_WIDTH / 2) + 5
        DataFrameVisualizer(self.parent_visualizer.display, (self._left_side_position, self._top_position), df, df.shape[0]).draw()

    def _is_valid_color(self, color: str):
        if color not in self.color_dict.keys():
            raise KeyError(f"The color {self.background_color} is not included, please try a color in: {list(self.color_dict.keys())}")
        return True

    def create_background(self):
        self._is_valid_color(self.background_color)
        # Draw the right grey area
        pygame.draw.rect(self.parent_visualizer.display, self.color_dict[self.background_color],
                         pygame.Rect(self.parent_visualizer.SCREEN_WIDTH / 2, 50,
                                     self.parent_visualizer.SCREEN_WIDTH / 2,
                                     self.parent_visualizer.SCREEN_HEIGHT - 50))

    def draw_interaction_matrix(self, adjacency_matrix):
        num_agents = len(adjacency_matrix)
        for i in range(num_agents):
            for j in range(i + 1, num_agents):  # We start from i+1 to avoid drawing lines twice
                if adjacency_matrix[i][j] > 0:
                    angle_i = 2 * math.pi * i / num_agents
                    x_i = self.parent_visualizer.SCREEN_WIDTH / 4 + self.parent_visualizer.agent_radius * math.cos(angle_i)
                    y_i = self.parent_visualizer.SCREEN_HEIGHT / 2 + self.parent_visualizer.agent_radius * math.sin(angle_i)

                    angle_j = 2 * math.pi * j / num_agents
                    x_j = self.parent_visualizer.SCREEN_WIDTH / 4 + self.parent_visualizer.agent_radius * math.cos(angle_j)
                    y_j = self.parent_visualizer.SCREEN_HEIGHT / 2 + self.parent_visualizer.agent_radius * math.sin(angle_j)

                    thickness = adjacency_matrix[i][j]
                    pygame.draw.line(self.parent_visualizer.display, (255, 255, 255), (int(x_i), int(y_i)), (int(x_j), int(y_j)),
                                     thickness)


class Plotter:
    def __init__(self, screen, position, size, x_data, y_data, title="Scatter Plot", xlabel="X-Axis", ylabel="Y-Axis"):
        self.screen = screen
        self.position = position
        self.size = size
        self.x_data = x_data
        self.y_data = y_data
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

    def draw_axes(self):
        pygame.draw.line(self.screen, (255, 255, 255), (self.position[0] + 50, self.position[1]), (self.position[0] + 50, self.position[1] + self.size[1]), 1)
        pygame.draw.line(self.screen, (255, 255, 255), (self.position[0], self.position[1] + self.size[1] - 50), (self.position[0] + self.size[0], self.position[1] + self.size[1] - 50), 1)

    def draw_data(self):
        for x, y in zip(self.x_data, self.y_data):
            pygame.draw.circle(self.screen, (0, 0, 255), (int(self.position[0] + 50 + x), int(self.position[1] + self.size[1] - 50 - y)), 5)

    def draw_labels(self):
        font = pygame.font.Font(None, 24)
        title_text = font.render(self.title, True, (255, 255, 255))
        xlabel_text = font.render(self.xlabel, True, (255, 255, 255))
        ylabel_text = font.render(self.ylabel, True, (255, 255, 255))
        self.screen.blit(title_text, (self.position[0] + self.size[0] // 2 - title_text.get_width() // 2, self.position[1] + 10))
        self.screen.blit(xlabel_text, (self.position[0] + self.size[0] // 2 - xlabel_text.get_width() // 2, self.position[1] + self.size[1] - 40))
        self.screen.blit(ylabel_text, (self.position[0] + 10, self.position[1] + self.size[1] // 2 - ylabel_text.get_height() // 2))

    def draw(self):
        self.draw_axes()
        self.draw_data()
        self.draw_labels()


class DataFrameVisualizer:
    def __init__(self, screen, position, df, rows, font_size=20, color=(255, 255, 255)):
        self.screen = screen
        self.position = position
        self.df = df
        self.rows = rows
        self.font_size = font_size
        self.color = color
        self.font = pygame.font.Font(None, self.font_size)
        self.line_height = self.font.get_linesize()

    def draw(self):
        x, y = self.position
        for i, col_name in enumerate(self.df.columns):
            text = self.font.render(str(col_name), True, self.color)
            self.screen.blit(text, (x + i*100, y))

        for j in range(self.rows):
            for i, value in enumerate(self.df.iloc[j]):
                text = self.font.render(str(value), True, self.color)
                self.screen.blit(text, (x + i*100, y + self.line_height*(j+1)))