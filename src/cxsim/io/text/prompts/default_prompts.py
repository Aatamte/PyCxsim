import os
from cxsim.io.text.prompts.prompt import PromptTemplate

# Get the directory of the current file
ASSET_PATH = os.path.dirname(os.path.abspath(__file__))

DEFAULT_SYSTEM_PROMPT = PromptTemplate(os.path.join(ASSET_PATH, "simple_system_prompt.txt"))

DEFAULT_COGNITIVE_PROMPT = PromptTemplate(os.path.join(ASSET_PATH, "cognitive_prompt.txt"))

DEFAULT_DECISION_PROMPT = PromptTemplate(os.path.join(ASSET_PATH, "decision_prompt.txt"))
