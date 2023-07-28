import pygame
import numpy as np
import asyncio
import math
import random
import pandas as pd
from src.visualization.app import Visualizer
#from src.environment.base_environment import Environment as ENV2


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

    async def async_step(self):
        # Simulate a time-consuming calculation
        await asyncio.sleep(0.01)
        # Simple simulation that generates random bids and asks
        self.bids = np.random.rand(10)
        self.asks = np.random.rand(10)
        self.adjacency_matrix = generate_random_adjacency_matrix(len(self.agent_names))
        return self.bids, self.asks, self.adjacency_matrix

    async def simulate_step(self):
        self.bids, self.asks, self.adjacency_matrix = await self.async_step()
        # Update graph history
        self.bid_history.append(np.average(self.bids))
        self.ask_history.append(np.average(self.asks))

        if self.enable_visualization:
            self.visualizer.visualize()

    def run(self):
        if self.enable_visualization:
            asyncio.run(self.visualizer.game_loop(self))


if __name__ == '__main__':
    # Initialize environment
    env = Environment(enable_visualization=False)

    env.run()

