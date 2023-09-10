from pydantic import BaseModel
from typing import List


def do_action(action: str, parameters: List[str]):
    return {"action": action, "parameters": parameters}


class Action(BaseModel):
    """do an action"""
    action: str
    parameters: List[str]
