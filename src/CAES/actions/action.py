from dataclasses import dataclass


@dataclass
class Action:
    action_id: int = 0
    step_taken: int = 0

    def create_prompt(self):
        pass
