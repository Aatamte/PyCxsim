import pygame
import pygame_menu
import math

from src.visualization.tabs.market_visualizer import MarketVisualizer
from src.visualization.tabs.environment_visualizer import EnvironmentTab

valid_visualizers = {
    "Market": MarketVisualizer
}


class Visualizer:
    def __init__(self, environment):
        pygame.init()
        self.environment = environment
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
        self.paused = False
        self.pause_button = pygame.Rect(50, 50, 100, 50)
        self.clock = pygame.time.Clock()
        # Set up some constants
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 800

        # Set up the display
        self.display = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT),  pygame.RESIZABLE)
        # Set up the fonts
        self.font_big = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)    # Smaller font for bids/asks
        # Number of agents to display
        self.num_agents = len(self.environment.agent_names)

        # Radius of the agent circle
        self.agent_radius = self.num_agents * 10
        self.max_line_thickness = 5
        self.tab_map = {
            "EnvironmentTab": EnvironmentTab(self)
        }
        self.tab_names = list(self.tab_map.keys())
        self.current_tab = self.tab_names[0]


    def reset(self):
        self.tab_map = {
            "EnvironmentTab": EnvironmentTab(self)
        }
        for artifact in self.environment.artifact_controller.artifacts.keys():
            if artifact in valid_visualizers.keys():
                self.tab_map[artifact] = valid_visualizers[artifact](self)

        self.tab_names = list(self.tab_map.keys())
        self.current_tab = self.tab_names[0]



    def draw_agent_connections(self, adjacency_matrix):
        num_agents = len(adjacency_matrix)
        for i in range(num_agents):
            for j in range(i+1, num_agents):  # We start from i+1 to avoid drawing lines twice
                if adjacency_matrix[i][j] > 0:
                    angle_i = 2 * math.pi * i / num_agents
                    x_i = self.SCREEN_WIDTH/4 + self.agent_radius * math.cos(angle_i)
                    y_i = self.SCREEN_HEIGHT/2 + self.agent_radius * math.sin(angle_i)

                    angle_j = 2 * math.pi * j / num_agents
                    x_j = self.SCREEN_WIDTH/4 + self.agent_radius * math.cos(angle_j)
                    y_j = self.SCREEN_HEIGHT/2 + self.agent_radius * math.sin(angle_j)

                    thickness = adjacency_matrix[i][j]
                    pygame.draw.line(self.display, (255, 255, 255), (int(x_i), int(y_i)), (int(x_j), int(y_j)), thickness)

    def clear_screen(self):
        self.display.fill((0, 0, 0))

    def draw_menu_bar(self):
        pygame.draw.rect(self.display, (200, 200, 200), pygame.Rect(0, 0, self.SCREEN_WIDTH, 50))
        title_text = self.font_big.render("Complex Adaptive Economic Simulator", True, (255, 255, 255))
        self.display.blit(title_text, (10, 10))
        # Draw the tabs
        for i, tab in enumerate(self.tab_names):
            name_length = len(tab)
            pygame.draw.rect(self.display, (150, 150, 150), pygame.Rect(self.SCREEN_WIDTH / 2 + i * 120, 0, 11 * name_length, 100))
            tab_text = self.font_big.render(tab, True, (0, 0, 0))
            self.display.blit(tab_text, (self.SCREEN_WIDTH / 2 + i * 150 + 10, 10))

    def draw_green_area_and_agents(self):
        pygame.draw.rect(self.display, self.color_dict["black"], pygame.Rect(0, 50, self.SCREEN_WIDTH/2, self.SCREEN_HEIGHT-50))
        # Draw the agents in a circle formation
        num_agents = len(self.environment.agent_names)
        self.agent_radius = num_agents * 10
        for i, agent in enumerate(self.environment.agents):
            angle = 2 * math.pi * i / num_agents
            x = self.SCREEN_WIDTH/4 + self.agent_radius * math.cos(angle)
            y = self.SCREEN_HEIGHT/2 + self.agent_radius * math.sin(angle)
            if agent.is_buyer:
                color = self.color_dict["green"]
            else:
                color = self.color_dict["red"]
            pygame.draw.circle(self.display, color, (int(x), int(y)), 15)
            # Draw the names
            name_text = self.font_small.render(str(agent.inventory) + str(agent.capital), True, (255, 255, 255))
            self.display.blit(name_text, (int(x)+20, int(y)))

    def draw_dialogue_screen(self):
        pygame.draw.rect(self.display, (200, 0, 0), pygame.Rect(self.SCREEN_WIDTH/2, 50, self.SCREEN_WIDTH/2, self.SCREEN_HEIGHT-50))

    def draw_titles_and_labels(self):
        # Draw axes for the graph
        pygame.draw.line(self.display, (255, 255, 255), (self.SCREEN_WIDTH/2, self.SCREEN_HEIGHT/2), (self.SCREEN_WIDTH, self.SCREEN_HEIGHT/2))  # x-axis
        pygame.draw.line(self.display, (255, 255, 255), (self.SCREEN_WIDTH/2, self.SCREEN_HEIGHT), (self.SCREEN_WIDTH/2, 50))  # y-axis

    def draw_pause_button(self):
        pygame.draw.rect(self.display, (255, 0, 0), self.pause_button)  # Draw the pause button as a red rectangle
        font = pygame.font.Font(None, 36)
        text = font.render('Pause' if not self.paused else 'Resume', True, (0, 0, 0))
        text_rect = text.get_rect(center=self.pause_button.center)  # Get the rectangular area covering the text
        self.display.blit(text, text_rect)  # Put the text in the center of the button

    def draw_bottom_panel(self):
        text = self.font_big.render("Bottom Panel", True, (255, 255, 255))
        text_rect = text.get_rect()
        self.display.blit(text, text_rect)

    def visualize(self):
        self.clear_screen()
        self.draw_menu_bar()
        self.draw_pause_button()
        self.draw_green_area_and_agents()

        self.tab_map[self.current_tab].create_background()
        self.tab_map[self.current_tab].draw(self.environment)

        self.draw_titles_and_labels()
        self.draw_pause_button()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.VIDEORESIZE:
                self.SCREEN_WIDTH, self.SCREEN_HEIGHT = event.size
                self.display = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.pause_button.collidepoint(
                        event.pos):  # Check if the click is within the bounds of the button
                    self.paused = not self.paused
                else:
                    x, y = event.pos
                    if y < 50:
                        for i, tab in enumerate(self.tab_names):
                            if x > self.SCREEN_WIDTH / 2 + i * 100 and x < self.SCREEN_WIDTH / 2 + (i + 1) * 100:
                                self.current_tab = tab
        return True

    async def game_loop(self, env):
        while self.handle_events():
            if not self.paused:
                await env.visualize_step()
            self.visualize()
            # Update the display
            pygame.display.flip()
            self.clock.tick(60)
