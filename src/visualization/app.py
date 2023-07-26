import pygame
import numpy as np
import asyncio
import math
import random
import pandas as pd

from src.visualization.utilities import DataFrameVisualizer, Plotter, VisualizerTab

df = pd.DataFrame({
    'Column1': ['A', 'B', 'C', 'D', 'E'],
    'Column2': [1, 2, 3, 4, 5],
    'Column3': [1.1, 2.2, 3.3, 4.4, 5.5],
})


class MarketVisualizer:
    def __init__(self, parent_visualizer):
        self.parent_visualizer = parent_visualizer
        self.graph_font = pygame.font.Font(None, 20)

    def draw_market(self, env):
        # Draw the right grey area
        pygame.draw.rect(self.parent_visualizer.display, (169, 169, 169),
                         pygame.Rect(self.parent_visualizer.SCREEN_WIDTH / 2, 50,
                                     self.parent_visualizer.SCREEN_WIDTH / 2,
                                     self.parent_visualizer.SCREEN_HEIGHT - 50))

        # Draw market data and graph
        self.draw_bid_ask_data(env)
        #self.draw_bid_ask_graph(env)

    def draw_bid_ask_data(self, env):
        combined = []
        for idx in range(len(env.bids)):
            combined.append([env.bids[idx], env.asks[idx]])
        # Draw the sorted bid and ask data
        env.bid_ask_history = combined.copy()
        for i, bid in enumerate(sorted(combined, key=lambda x: x[0])):
            bid_text = self.graph_font.render(f'Bid: {bid[0]} Ask: {bid[1]}', True, (0, 0, 0))
            self.parent_visualizer.display.blit(bid_text, (self.parent_visualizer.SCREEN_WIDTH / 2 + 10, 60 + i * 20))

    def draw_bid_ask_graph(self, env):
        # Plot bid/ask history
        for i in range(1, len(env.bid_ask_history)):
            pygame.draw.line(self.parent_visualizer.display, (255, 0, 0),
                             (self.parent_visualizer.SCREEN_WIDTH / 2 + i, env.bid_ask_history[i - 1][0]),
                             (self.parent_visualizer.SCREEN_WIDTH / 2 + i + 1, env.bid_ask_history[i][0]), 2)
            pygame.draw.line(self.parent_visualizer.display, (0, 255, 0),
                             (self.parent_visualizer.SCREEN_WIDTH / 2 + i, env.bid_ask_history[i - 1][1]),
                             (self.parent_visualizer.SCREEN_WIDTH / 2 + i + 1, env.bid_ask_history[i][1]), 2)


class EnvironmentInfo(VisualizerTab):
    def __init__(self, parent_visualizer):
        super(EnvironmentInfo, self).__init__(parent_visualizer)
        self.graph_font = pygame.font.Font(None, 20)

    def draw_info(self, env):
        # Draw the right grey area
        pygame.draw.rect(self.parent_visualizer.display, (169, 169, 169),
                         pygame.Rect(self.parent_visualizer.SCREEN_WIDTH / 2, 50,
                                     self.parent_visualizer.SCREEN_WIDTH / 2,
                                     self.parent_visualizer.SCREEN_HEIGHT - 50))
        text = self.graph_font.render(f'Number of agents: {len(env.agent_names)}', True, (0, 0, 0))
        self.parent_visualizer.display.blit(text, (self.parent_visualizer.SCREEN_WIDTH / 2 + 10, 50))
        DataFrameVisualizer(self.parent_visualizer.display, (self.parent_visualizer.SCREEN_WIDTH / 2, 50), df, 5).draw()


class Visualizer:
    def __init__(self, environment):
        pygame.init()
        self.environment = environment

        self.paused = False
        self.pause_button = pygame.Rect(50, 50, 100, 50)
        self.clock = pygame.time.Clock()
        # Set up some constants
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1200, 800
        # Set up the display
        self.display = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT),  pygame.RESIZABLE)
        # Set up the fonts
        self.font_big = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18) # Smaller font for bids/asks
        # Number of agents to display
        self.num_agents = 10
        # Radius of the agent circle
        self.agent_radius = 150
        self.max_line_thickness = 5
        self.market_visualizer = MarketVisualizer(self)
        self.info_visualizer = EnvironmentInfo(self)
        self.tabs = ["Market", "Dialogue", "info"]
        self.current_tab = self.tabs[0]

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
        for i, tab in enumerate(self.tabs):
            pygame.draw.rect(self.display, (150, 150, 150), pygame.Rect(self.SCREEN_WIDTH / 2 + i * 100, 0, 100, 50))
            tab_text = self.font_big.render(tab, True, (0, 0, 0))
            self.display.blit(tab_text, (self.SCREEN_WIDTH / 2 + i * 100 + 10, 10))

    def draw_green_area_and_agents(self):
        pygame.draw.rect(self.display, (0, 100, 0), pygame.Rect(0, 50, self.SCREEN_WIDTH/2, self.SCREEN_HEIGHT-50))
        # Draw the agents in a circle formation
        num_agents = len(self.environment.agent_names)
        for i in range(num_agents):
            angle = 2 * math.pi * i / num_agents
            x = self.SCREEN_WIDTH/4 + self.agent_radius * math.cos(angle)
            y = self.SCREEN_HEIGHT/2 + self.agent_radius * math.sin(angle)
            pygame.draw.circle(self.display, (0, 0, 255), (int(x), int(y)), 20)
            # Draw the names
            name_text = self.font_small.render(self.environment.agent_names[i], True, (255, 255, 255))
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
        self.draw_agent_connections(env.adjacency_matrix)
        if self.current_tab == 'Market':
            self.market_visualizer.draw_market(self.environment)
        elif self.current_tab == "info":
            self.info_visualizer.draw_info(self.environment)
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
                        for i, tab in enumerate(self.tabs):
                            if x > self.SCREEN_WIDTH / 2 + i * 100 and x < self.SCREEN_WIDTH / 2 + (i + 1) * 100:
                                self.current_tab = tab
        return True

    async def game_loop(self, env):
        while self.handle_events():
            if not self.paused:
                await env.simulate_step()
            self.visualize()
            # Update the display
            pygame.display.flip()
            self.clock.tick(60)


def generate_random_adjacency_matrix(size):
    # Generate a random adjacency matrix with values from 0 to max_line_thickness
    adjacency_matrix = [[random.randint(0, 1) for _ in range(size)] for _ in range(size)]

    # Since adjacency matrix is symmetric, we copy the lower triangle to the upper triangle
    for i in range(size):
        for j in range(i+1, size):
            adjacency_matrix[i][j] = adjacency_matrix[j][i]

    return adjacency_matrix


class Environment:
    def __init__(self, enable_visualization):
        self.enable_visualization = enable_visualization
        self.visualizer = Visualizer(self) if enable_visualization else None
        # Graph history
        self.bid_history = []
        self.ask_history = []
        self.bid_ask_history = []
        self.graph_history_size = 100
        self.agent_names = ["Alice", "Bob", "Charlie", "John", "Aaron", "Sophia"]
        self.adjacency_matrix = generate_random_adjacency_matrix(len(self.agent_names))

    async def step(self):
        # Simulate a time-consuming calculation
        await asyncio.sleep(0.01)
        # Simple simulation that generates random bids and asks
        self.bids = np.random.rand(10)
        self.asks = np.random.rand(10)
        self.adjacency_matrix = generate_random_adjacency_matrix(len(self.agent_names))
        return self.bids, self.asks, self.adjacency_matrix

    async def simulate_step(self):
        self.bids, self.asks, self.adjacency_matrix = await self.step()
        # Update graph history
        self.bid_history.append(np.average(self.bids))
        self.ask_history.append(np.average(self.asks))

        # If the graph history is too long, remove the oldest elements
        #if len(self.bid_history) > self.graph_history_size:
         #   self.bid_history.pop(0)
        #if len(self.ask_history) > self.graph_history_size:
        #    self.ask_history.pop(0)

        if self.enable_visualization:
            self.visualizer.visualize()

    def run(self):
        asyncio.run(self.visualizer.game_loop(self))


if __name__ == '__main__':
    # Initialize environment
    env = Environment(enable_visualization=True)

    env.run()
