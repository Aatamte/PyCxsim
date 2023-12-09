from cxsim.artifacts.artifact import Artifact
from dataclasses import dataclass


@dataclass
class Move:
    """Move action, valid parameters for direction are:
    - up: increase y position by 1 Example: (0, 1) -> (0, 2)
    - down: decrease y position by 1 Example: (0, 1) -> (0, 0)
    - right: increase x position by 1 Example: (0, 1) -> (1, 1)
    - left: decrease x position by 1 Example: (1, 1) -> (0, 1)
    """
    direction: str


@dataclass
class GridworldQuery:
    """Displays the current map with positions of all the agents, valid parameter for level are ["full"]"""
    level: str


class Block:
    def __init__(self):
        pass


class Gridworld(Artifact):
    """The Gridworld artifact represents a two-dimensional, square grid environment, often used in reinforcement learning and AI simulations. The grid is a spatio-temporal world where each cell or block is identified using a coordinate system. The origin, (0, 0), is located at the bottom-left corner of the grid. Additionally, you cannot move into the same position as another agent."""
    def __init__(self, x_size: int):
        super(Gridworld, self).__init__("Gridworld")
        self.x_size = x_size
        self.y_size = x_size

        #self.query_space.append(GridworldQuery)
        self.action_space.append(Move)

    def to_text(self, this_agent=None):
        # Initialize the grid with dots
        grid = [['.' for _ in range(self.x_size)] for _ in range(self.y_size)]

        # Define a list of uppercase letters for agent representation
        letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

        # Create a dictionary to store agent-letter mapping
        agent_letter_map = {}

        # Update the grid with agent positions
        for idx, agent in enumerate(self.environment.agents):
            name = agent.name
            if agent == this_agent:
                grid[agent.y_pos][agent.x_pos] = 'X'  # 'X' for the special agent
                agent_letter_map[name] = ('X', agent.x_pos, agent.y_pos)
            else:
                letter = letters[idx % len(letters)]  # Get a letter for the agent
                grid[agent.y_pos][agent.x_pos] = letter
                agent_letter_map[name] = (letter, agent.x_pos, agent.y_pos)

        # Add x-axis integer positions at the top
        header = '  ' + ' '.join(map(str, range(self.x_size)))

        # Add y-axis integer positions on the left side and convert the grid to a string representation
        # Reverse the order of the rows for the desired coordinate system
        grid_text = [header] + ['{} {}'.format(self.y_size - 1 - i, ' '.join(row)) for i, row in
                                enumerate(reversed(grid))]

        # Add the key for agent-letter mapping at the bottom
        key_text = ["\nKey:"]
        if this_agent:
            key_text.append("{} (X): ({}, {})".format(this_agent.name, this_agent.x_pos, this_agent.y_pos))
        key_text += ["{} ({}): ({}, {})".format(agent, letter, x, y) for agent, (letter, x, y) in
                     agent_letter_map.items() if agent != this_agent.name]

        return '\n'.join(grid_text + key_text)

    def process_query(self, agent, query):
        grid_text = self.to_text(special_agent=agent)
        description = grid_text + "\nA: Other agents, S: You, .: empty spaces"
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
                return "Move interferes with another agent!"

        # Update the agent's position
        agent.x_pos = new_x_pos
        agent.y_pos = new_y_pos
        print(agent.x_pos, agent.y_pos)

        return f"Your current position is now: {str((agent.x_pos, agent.y_pos))}\n" + self.to_text(this_agent=agent)

    def set_up(self, environment):
        self.environment = environment

    def reset(self, environment):
        pass