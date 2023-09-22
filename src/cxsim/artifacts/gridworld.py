from src.cxsim.artifacts.artifact import Artifact
from dataclasses import dataclass
from src.cxsim.agents.agent import Agent


@dataclass
class Move:
    """Move action, valid parameters are ["up", "down", "right", "left"]"""
    direction: str


@dataclass
class GridworldQuery:
    """Displays the current map with positions of all the agents, valid parameter for level are ["full"]"""
    level: str


class Block:
    def __init__(self):
        pass


class Gridworld(Artifact):
    def __init__(self, x_size: int):
        super(Gridworld, self).__init__("Gridworld")
        self.x_size = x_size
        self.y_size = x_size

        self.query_space.append(GridworldQuery)
        self.action_space.append(Move)

    def to_text(self, special_agent=None):
        # Initialize the grid with dots
        grid = [['.' for _ in range(self.x_size)] for _ in range(self.y_size)]

        # Update the grid with agent positions
        for agent in self.environment.agents:
            if agent == special_agent:
                grid[agent.y_pos][agent.x_pos] = 'O'  # 'S' for the special agent
            else:
                grid[agent.y_pos][agent.x_pos] = 'A'

        # Convert the grid to a string representation
        grid_text = '\n'.join([' '.join(row) for row in grid])

        return grid_text

    def process_query(self, agent, query):
        grid_text = self.to_text(special_agent=agent)
        description = grid_text  + "\nA: Other agents, S: You, .: empty spaces"
        return description

    def process_action(self, agent, action):
        print(agent, action)
        print(agent.x_pos, agent.y_pos)
        if isinstance(action, Move):
            if action.direction == "up":
                if agent.y_pos > 0:
                    agent.y_pos -= 1
            elif action.direction == "down":
                if agent.y_pos < self.y_size - 1:
                    agent.y_pos += 1

            elif action.direction == "right":
                if agent.x_pos < self.x_size - 1:
                    agent.x_pos += 1
            elif action.direction == "left":
                if agent.x_pos > 0:
                    agent.x_pos -= 1
            else:
                pass
            print(agent.x_pos, agent.y_pos)

    def set_up(self, environment):
        self.environment = environment

    def reset(self, environment):
        pass