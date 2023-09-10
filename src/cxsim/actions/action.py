from pydantic import BaseModel


def do_action(action: str, parameters: dict):
    return {"action": action, "parameters": parameters}


class Action(BaseModel):
    """do an action"""
    action: str
    parameters: dict
