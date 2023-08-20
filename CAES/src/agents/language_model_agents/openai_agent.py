from CAES.src.agents.language_model_agents.language_model_agent import LanguageModelAgent
import openai
import ast
import json


class OAIAgent(LanguageModelAgent):
    def __init__(
            self,
            model_id: str = "gpt-3.5-turbo-0613"
    ):
        super(OAIAgent, self).__init__()
        self.model_id = model_id

        self.language_model_logs = []

    def receives_message(self, text):
        self.messages.append(
            {
                "role": "user",
                "content": text
            }
        )
        di = {'None': 'None'}
        self.create_ChatCompletion()

    def execute_action(self):
        self.create_ChatCompletion()
        response = self.messages[-1]["content"]
        if "\n" in response:
            action_string = response.strip("\n")[0]
        else:
            action_string = response
        action_dict = ast.literal_eval(action_string)
        print(action_dict)
        return action_dict



