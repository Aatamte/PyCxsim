from src.cxsim.agents.agent import Agent
from queue import Queue

# NOTES
#
# a language model agent should have the following traits:
#   - strict enforcement of following actions specified by the environment
#       - class would automatically recall select action if the agent took an invalid action


class LanguageModelAgent(Agent):
    def __init__(self, local: bool = False, temperature: float = 1.0):
        super(LanguageModelAgent, self).__init__()
        self.local: bool = local
        self.temperature: float = temperature

        self.messages = []

        self.system_prompt = None

        self.n_unfollowed_actions: int = 0

        self.usage_statistics = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

    def execute_api_call(self, api_callable):
        pass

    def set_up(self):
        pass

    def retry_select_action(self):
        self.n_unfollowed_actions += 1

    def execute_query(self):
        pass

    def execute_action(self):
        pass



if __name__ == '__main__':
    pass