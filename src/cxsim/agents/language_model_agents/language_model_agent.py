from src.cxsim.agents.agent import Agent
from src.cxsim.agents.connnections.language_model_connection import LanguageModelAPIConnection

# NOTES
#
# a language model agent should have the following traits:
#   - strict enforcement of following actions specified by the environment
#       - class would automatically recall select action if the agent took an invalid action


class LanguageModelAgent(Agent):
    def __init__(self, local: bool = False, temperature: float = 1.0):
        super(LanguageModelAgent, self).__init__()
        self.connection = LanguageModelAPIConnection()
        self.local: bool = local
        self.temperature: float = temperature

        self.messages = []

        self.n_unfollowed_actions: int = 0

        self.usage_statistics = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

    def set_up(self):
        pass

    def send(self, *args, **kwargs):
        return self.connection.send(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.connection.send(*args, **kwargs)

    def add_message(self, role: str, content: str, function_name: str = None):
        """Add a message to the agents messaging dictionary"""
        self.connection.add_message(role=role, content=content, function_name=function_name)




if __name__ == '__main__':
    pass