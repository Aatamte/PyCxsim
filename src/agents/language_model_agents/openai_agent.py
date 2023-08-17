from src.agents.language_model_agents.language_model_agent import LanguageModelAgent
import openai


class OAIAgent(LanguageModelAgent):
    def __init__(
            self,
            model_id: str = "gpt-3.5-turbo-0613"
    ):
        super(OAIAgent, self).__init__()
        self.model_id = model_id

        self.language_model_logs = []

