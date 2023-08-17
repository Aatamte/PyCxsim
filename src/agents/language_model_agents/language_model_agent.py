from src.agents.agent import Agent
from src.prompts.prompt import Prompt
# NOTES
#
# a language model agent should have the following features:
#   - strict enforcement of following actions specified by the environment
#       - class would automatically recall select action if the agent took an invalid action


def parse_json_response(response):
    pass


class LanguageModelAgent(Agent):
    def __init__(self, local: bool = False, temperature: float = 1.0):
        super(LanguageModelAgent, self).__init__()
        self.local: bool = local
        self.temperature: float = temperature
        self.messages = []

        self.system_prompt: str = ""

        self.n_unfollowed_actions: int = 0

        self.usage_statistics = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

    def retry_select_action(self):
        self.n_unfollowed_actions += 1
        self.select_action()

    def select_action(self):
        pass

    def request(self):
        pass

    def set_up(self):
        pass

    def get_observation(self, observation):
        self.messages.append(
            {
                "role": "user",
                "content": observation
            }
        )

    def add_set_up_prompt(self, prompt: Prompt, order_urgency: int):

        pass


if __name__ == '__main__':
    pass