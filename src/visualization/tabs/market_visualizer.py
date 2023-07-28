import pygame
from src.visualization.utilities import Tab, DataFrameVisualizer


class MarketVisualizer(Tab):
    def __init__(self, parent_visualizer):
        super(MarketVisualizer, self).__init__(parent_visualizer)
        self.name = "Market"
        self.market = self.parent_visualizer.environment.artifact_controller.artifacts["Market"]

    def draw(self, env):
        # Draw market data and graph
        self.write_dataframe(self.market.history()[::-1].head(10))
        int_matrix = self.market.get_adjacency_matrix()
        self.draw_interaction_matrix(int_matrix)

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
