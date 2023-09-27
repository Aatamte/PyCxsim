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
                grid[agent.y_pos][agent.x_pos] = 'O'  # 'O' for the special agent
            else:
                grid[agent.y_pos][agent.x_pos] = 'X'

        # Add x-axis integer positions at the top
        header = '  ' + ' '.join(map(str, range(self.x_size)))

        # Add y-axis integer positions on the left side and convert the grid to a string representation
        # Reverse the order of the rows for the desired coordinate system
        grid_text = [header] + ['{} {}'.format(self.y_size - 1 - i, ' '.join(row)) for i, row in enumerate(reversed(grid))]

        return '\n'.join(grid_text)

    def process_query(self, agent, query):
        grid_text = self.to_text(special_agent=agent)
        description = grid_text  + "\nA: Other agents, S: You, .: empty spaces"
        return description

    def process_action(self, agent, action):
        print(agent, action)
        print(agent.x_pos, agent.y_pos)

        new_x_pos = agent.x_pos
        new_y_pos = agent.y_pos

        if isinstance(action, Move):
            if action.direction == "up" and agent.y_pos < self.y_size - 1:
                new_y_pos += 1
            elif action.direction == "down" and agent.y_pos > 0:
                new_y_pos -= 1
            elif action.direction == "right" and agent.x_pos < self.x_size - 1:
                new_x_pos += 1
            elif action.direction == "left" and agent.x_pos > 0:
                new_x_pos -= 1

        # Check if the new position interferes with another agent's position
        for other_agent in self.environment.agents:
            if other_agent != agent and other_agent.x_pos == new_x_pos and other_agent.y_pos == new_y_pos:
                print("Move interferes with another agent!")
                return  # Exit the function without updating the agent's position

        # Update the agent's position
        agent.x_pos = new_x_pos
        agent.y_pos = new_y_pos
        print(agent.x_pos, agent.y_pos)

    def set_up(self, environment):
        self.environment = environment

    def reset(self, environment):
        pass