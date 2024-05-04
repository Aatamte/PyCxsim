from cxsim.artifacts.artifact import Artifact
from cxsim.agents.actions.action import Action
from cxsim.environment.database.cx_data_types import CxDataType
from typing import Dict, List
import random


class Move(Action):
    """Move action, valid parameters for direction are:
    - up: increase y position by 1 Example: (0, 1) -> (0, 2)
    - down: decrease y position by 1 Example: (0, 1) -> (0, 0)
    - right: increase x position by 1 Example: (0, 1) -> (1, 1)
    - left: decrease x position by 1 Example: (1, 1) -> (0, 1)

    for example, use
    Move(direction="up")
    """
    direction: str = None


class Block:
    def __init__(self, name: str, color: tuple = (0, 0, 0), can_occupy: bool = True, is_goal: bool = False, x_pos: int = 0, y_pos: int = 0):
        self.name = name
        self.color = color
        self.can_occupy = can_occupy
        self.is_goal = is_goal
        self.x_pos = x_pos  # Position x
        self.y_pos = y_pos  # Position y
        self.content = None

    def interact(self, agent):
        # Define interaction behavior here
        pass

    def render(self):
        pass

    def __str__(self):
        # Single-character representation of the block's content or a space if empty
        content_repr = str(self.content)[:5] if self.content else '_____'
        # Return a string that visually represents the block as a square
        return f"{content_repr}"

    def __setitem__(self, key, value):
        """Set the content of the block directly."""
        self.content = value

    @property
    def is_empty(self):
        """Check if the block is empty (no content)."""
        return self.content is None

    @property
    def to_item(self):
        """Returns a dictionary representation of the block."""
        # Format color as a hex string if it's a tuple of RGB values
        color_hex = '#{:02x}{:02x}{:02x}'.format(*self.color) if isinstance(self.color, tuple) else self.color
        return {
            "position": f"({self.x_pos}, {self.y_pos})",
            "color": color_hex,
            "content": str(self.content) if self.content else "Empty",
            "can_occupy": self.can_occupy,
            "is_goal": self.is_goal
        }

    def copy(self):
        """Create and return a copy of the block."""
        return Block(
            name=self.name,
            color=self.color,
            can_occupy=self.can_occupy,
            is_goal=self.is_goal,
            x_pos=self.x_pos,
            y_pos=self.y_pos
        )


class Gridworld(Artifact):
    """The Gridworld artifact represents a two-dimensional, square grid environment, often used in reinforcement learning and AI simulations. The grid is a spatio-temporal world where each cell or block is identified using a coordinate system. The origin, (0, 0), is located at the bottom-left corner of the grid. Additionally, you cannot move into the same position as another agent."""

    def __init__(
            self,
            x_size: int = 0,
            y_size: int = 0
    ):
        super(Gridworld, self).__init__("Gridworld")

        self.size_factor = 5

        self.x_size: int = x_size
        self.y_size: int = y_size
        self.z_size: int = 0

        if self.x_size == 0:
            self.x_size = 15

        if self.y_size == 0:
            self.y_size = 15

        self.grid: List[List[Block]] = self.create_grid()

        self.action_space.append(Move)

        self.agent_position_map: Dict[str, tuple] = {}

    def step(self):
        pass

    def compile(self, environment):
        for agent in environment.agents:
            self.place_agent(agent)

    def create_grid(self):
        return [[Block(name='Empty', x_pos=x, y_pos=y, color=(255, 255, 255)) for y in range(self.y_size)] for x in range(self.x_size)]

    def place_agent(self, agent, spacing: int = 1, verbose: bool = False):
        # Generate all possible positions
        all_positions = [(x, y) for x in range(self.x_size) for y in range(self.y_size)]
        if verbose:
            print(f"Generated all possible positions: {all_positions}")

        # Shuffle the list of positions to ensure randomness
        random.shuffle(all_positions)
        if verbose:
            print(f"Shuffled positions: {all_positions}")

        while all_positions:
            # Pop a random position from the list
            x_pos, y_pos = all_positions.pop()
            if verbose:
                print(f"Trying position: {(x_pos, y_pos)}")

            # Check if the current position can be occupied
            if not self.grid[x_pos][y_pos].can_occupy:
                if verbose:
                    print(f"Position {(x_pos, y_pos)} cannot be occupied. Skipping.")
                continue

            # Generate a list of neighboring positions within 'spacing'
            neighbors = [
                (x, y)
                for x in range(max(0, x_pos - spacing), min(self.x_size, x_pos + spacing + 1))
                for y in range(max(0, y_pos - spacing), min(self.y_size, y_pos + spacing + 1))
                if (x, y) != (x_pos, y_pos)  # Exclude the position itself
            ]
            if verbose:
                print(f"Generated neighboring positions for spacing {spacing}: {neighbors}")

            # Check if any neighbor positions are already occupied by other agents or cannot be occupied
            if not any(not self.grid[x][y].can_occupy or self.grid[x][y].content for x, y in neighbors):
                # Directly set the agent in the grid using __setitem__
                self[x_pos, y_pos] = agent

                # Update the agent_position_map with the new position
                self.agent_position_map[agent.name] = (x_pos, y_pos)

                if verbose:
                    print(f"Placed agent at: {(x_pos, y_pos)}")
                return

        # If we reach here, no suitable position was found
        if verbose:
            print("Unable to assign a valid position for the agent with the specified spacing.")
        raise ValueError("Unable to assign a valid position for the agent with the specified spacing.")

    def display(self):
        # Determine the width of each cell based on the content length plus padding
        cell_width = 7  # Adjust this based on the maximum expected content length

        # Top border of the grid
        display_str = ""

        for y in range(self.y_size):  # Iterate from top to bottom
            row_str = "|"
            for x in range(self.x_size):  # Iterate from left to right
                block = self.grid[x][y]
                block_str = str(block)
                # Pad the block string to ensure it fits the cell width uniformly
                block_str_padded = block_str.center(cell_width - 2)  # Adjust padding based on the cell width
                row_str += f"{block_str_padded}|"  # Append each block's representation within cell borders
            display_str += row_str + "\n"

        return display_str

    def process_action(self, agent, action):
        verbose = False
        if verbose:
            print(f"Processing action for {agent.name}: {action.direction}")

        # Validate the action type
        if not isinstance(action, Move):
            if verbose:
                print("Invalid action type.")
            return "Invalid action type."

        # Calculate the potential new position based on the action
        new_x_pos, new_y_pos = agent.x_pos, agent.y_pos
        if action.direction == "up" and agent.y_pos < self.y_size - 1:
            new_y_pos += 1
        elif action.direction == "down" and agent.y_pos > 0:
            new_y_pos -= 1
        elif action.direction == "right" and agent.x_pos < self.x_size - 1:
            new_x_pos += 1
        elif action.direction == "left" and agent.x_pos > 0:
            new_x_pos -= 1

        if verbose:
            print(f"New position attempt: ({new_x_pos}, {new_y_pos})")

        # Check if the new position is within grid bounds
        if not (0 < new_x_pos <= self.x_size and 0 < new_y_pos <= self.y_size):
            if verbose:
                print("Move out of grid bounds.")
            return "Move out of grid bounds."

        # Check for collisions with other agents using the Block's content
        if self.grid[new_x_pos][new_y_pos].content is not None:
            if verbose:
                print("Move interferes with another agent!")
            return "Move interferes with another agent!"

        # Check for collisions with other agents using the Block's content
        if not self.grid[new_x_pos][new_y_pos].can_occupy:
            if verbose:
                print("Block is not passable!")
            return "Move interferes with another agent!"

        if verbose:
            print(f"Move successful. {agent.name} moved to ({new_x_pos}, {new_y_pos})")

        # Update the agent's position in the grid and the agent_position_map
        self.grid[agent.x_pos][agent.y_pos].content = None
        self.grid[new_x_pos][new_y_pos].content = agent
        self.agent_position_map[agent.name] = (new_x_pos, new_y_pos)

        return f"Your current position is now: {(agent.x_pos, agent.y_pos)}"

    def reset(self, environment):
        pass

    def get_agent_position(self, agent_name):
        """Retrieve the position of an agent by their name."""
        if agent_name in self.agent_position_map:
            return self.agent_position_map[agent_name]
        else:
            return None

    def get_blocks(self):
        blocks_list = []
        for row in self.grid:  # Iterate through each row in the grid
            for block in row:  # Iterate through each block in the row
                blocks_list.append(block.to_item)  # Use the to_item property from Block class
        return blocks_list

    def add_wall(self, position_from, position_to, block: Block = None):
        if block is None:
            block = Block(name='Wall', color=(128, 128, 128), can_occupy=False)

        x_from, y_from = position_from
        x_to, y_to = position_to

        # Ensure the positions are within the grid bounds
        if not (0 <= x_from < self.x_size and 0 <= y_from < self.y_size):
            raise ValueError(f"Invalid position_from: {position_from}")
        if not (0 <= x_to < self.x_size and 0 <= y_to < self.y_size):
            raise ValueError(f"Invalid position_to: {position_to}")

        # Determine the direction of the wall
        if x_from == x_to:
            # Vertical wall
            for y in range(min(y_from, y_to), max(y_from, y_to) + 1):
                self.grid[x_from][y].name = "Wall"
                self.grid[x_from][y].content = "Wall"
                self.grid[x_from][y].can_occupy = False
                self.grid[x_from][y].color = (128, 128, 128)
        elif y_from == y_to:
            # Horizontal wall
            for x in range(min(x_from, x_to), max(x_from, x_to) + 1):
                self.grid[x][y_from].content = "Wall"
                self.grid[x][y_from].name = "Wall"
                self.grid[x][y_from].can_occupy = False
                self.grid[x][y_from].color = (128, 128, 128)
        else:
            raise ValueError("Invalid wall positions. The wall must be either vertical or horizontal.")

    def replace_block(self, x, y, new_block: Block):
        new_block.x_pos = x
        new_block.y_pos = y
        self.grid[x][y] = new_block

    def __getitem__(self, key):
        """Get the block at the specified grid position."""
        x, y = key  # Extract x, y coordinates from the key
        return self.grid[x][y].content

    def __setitem__(self, key, value):
        """Set the item at grid position specified by key."""
        x, y = key
        self.grid[x][y].content = value
