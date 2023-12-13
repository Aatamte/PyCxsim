from cxsim.prompts.prompt import PromptTemplate
import pathlib

ASSET_PATH = pathlib.Path(__file__).parent

DEFAULT_SYSTEM_PROMPT = PromptTemplate(ASSET_PATH.joinpath("system_prompt.txt").__str__())

DEFAULT_COGNITIVE_PROMPT = PromptTemplate(ASSET_PATH.joinpath("cognitive_prompt.txt").__str__())

DEFAULT_DECISION_PROMPT = PromptTemplate(ASSET_PATH.joinpath("decision_prompt.txt").__str__())

