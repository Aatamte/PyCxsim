import pygame


class VisualizerTab:
    def __init__(self, parent_visualizer):
        self.parent_visualizer = parent_visualizer


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