from CAES.src.agents.agent import Agent
from CAES.src.prompts.prompt import Prompt
import openai
import asyncio

# NOTES
#
# a language model agent should have the following features:
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


    def complete_ChatCompletion(self):
        return openai.ChatCompletion.create(model=self.model_id, messages=self.messages,
                                                  temperature=self.temperature)

    def create_ChatCompletion(self):
        response = self.complete_ChatCompletion()
        self.messages.append(
            {'role': response.choices[0].message.role, 'content': response.choices[0].message.content}
        )
        print(self.messages)

    def set_up(self):
        self.messages.append(
            {
                "role": "system",
                "content": self.system_prompt.content
            }
        )
        self.create_ChatCompletion()

    def retry_select_action(self):
        self.n_unfollowed_actions += 1

    def execute_query(self):
        pass

    def execute_action(self):
        pass



if __name__ == '__main__':
    pass