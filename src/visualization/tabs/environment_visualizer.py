from src.visualization.utilities import Tab, DataFrameVisualizer
import pygame
import pandas as pd


df = pd.DataFrame({
    'Column1': ['A', 'B', 'C', 'D', 'E'],
    'Column2': [1, 2, 3, 4, 5],
    'Column3': [1.1, 2.2, 3.3, 4.4, 5.5],
})


class EnvironmentTab(Tab):
    def __init__(self, parent_visualizer):
        super(EnvironmentTab, self).__init__(parent_visualizer)
        self.name = "EnvironmentTab"
        self.background_color = "gray"

    def draw(self, env):
        self.write_text(f"Number of agents: {len(env.agent_names)}")


