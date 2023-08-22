from src.CAES.agents.language_model_agents.language_model_agent import LanguageModelAgent
import ast
import openai
import threading
import json
from queue import Queue


class OAIAgent(LanguageModelAgent):
    def __init__(
            self,
            model_id: str = "gpt-3.5-turbo-0613"
    ):
        super(OAIAgent, self).__init__()
        self.model_id = model_id
        self.language_model_logs = []

    def execute_action(self):
        self.create_ChatCompletion()
        response = self.messages[-1]["content"]
        if "\n" in response:
            action_string = response.strip("\n")[0]
        else:
            action_string = response
        action_dict = ast.literal_eval(action_string)
        print(action_dict)
        print(type(action_dict))
        if action_dict["action"] == "skip":
            pass
        else:
            if not isinstance(action_dict, dict):
                action_dict["action"] = json.loads(action_dict["action"])
        print(action_dict)
        return action_dict

    def complete_ChatCompletion(self):
        response = openai.ChatCompletion.create(
            model=self.model_id,
            messages=self.messages,
            temperature=self.temperature
        )
        self.messages.append(
            {'role': response.choices[0].message.role, 'content': response.choices[0].message.content}
        )

    def get_result(self):
        pass

    def create_ChatCompletion(self):
        self.complete_ChatCompletion()

    def set_up(self):
        self.messages.append(
            {
                "role": "system",
                "content": self.system_prompt.content
            }
        )
        self.create_ChatCompletion()