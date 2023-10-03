from dataclasses import dataclass


@dataclass
class Skip:
    value: str = "None"


STANDARD_ACTIONS = [
    Skip
]
