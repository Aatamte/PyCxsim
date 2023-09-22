from src.cxsim.artifacts.artifact import Artifact
from dataclasses import dataclass
from src.cxsim.agents.agent import Agent


@dataclass
class Move:
    """Move action, valid parameters are ["up", "down", "right", "left"]"""
    direction: str


class Block:
    def __init__(self):
        pass


class GridWorld(Artifact):
    def __init__(self):
        super(GridWorld, self).__init__("GridWorld")
        self.action_space.append(Move)

    def process_query(self, agent, query):
        pass

    def process_action(self, agent, action):
        print(agent, action)
        print(agent.x_pos, agent.y_pos)
        if isinstance(action, Move):
            if action.direction == "up":
                agent.y_pos += 1
            elif action.direction == "down":
                agent.y_pos += 1
            elif action.direction == "right":
                agent.x_pos += 1
            elif action.direction == "left":
                agent.x_pos -= 1
            else:
                pass
            print(agent.x_pos, agent.y_pos)


    def set_up(self, environment):
        pass

    def reset(self, environment):
        pass