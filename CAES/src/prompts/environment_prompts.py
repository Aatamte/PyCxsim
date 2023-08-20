from CAES.src.prompts.prompt import Prompt

ENVIRONMENT_PROMPT = Prompt(
    """
    You are an AI agent in a multi-agent simulation. The simulation is made up of artifacts, which govern the logic of the simulation
    """
)

RULES_PROMPT = Prompt(
    """
    
    """
)


ACTIONS_PROMPT = Prompt(
    """
    Once you choose an action to take, put the action within a JSON format.
    The following actions are valid actions in the simulation:
    """
)

