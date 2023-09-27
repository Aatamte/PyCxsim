import openai

from src.cxsim.agents.language_model_agents.language_model_agent import LanguageModelAgent
from cxsim.utilities.background_jobs.decorators import background_task
from src.cxsim.utilities.convert_string_to_json import string_to_dict
import json
import asyncio
import re


def parse_value(val):
    if not isinstance(val, str):  # Ensure val is a string
        return val

    if re.match(r'^-?\d+$', val):  # Checks if the string is a whole number (positive or negative)
        return int(val)

    # You can add more regex checks here for other numerical types, e.g., floats
    return val


class OAIAgent(LanguageModelAgent):
    def __init__(self, model_id: str = "gpt-3.5-turbo-0613"):
        super(OAIAgent, self).__init__()
        self.model_id = model_id
        self.language_model_logs = []
        self.temperature = 0.85

        self.keep_last_n = 1000

    def step(self):
        if len(self.messages) <= self.keep_last_n + 1:
            pass
        else:
            self.messages = [self.messages[0]] + self.messages[-self.keep_last_n:]

    def execute_action(self):
        self.create_ChatCompletion()
        return None

    def execute_query(self):
        self.create_ChatCompletion()
        return None

    def create_ChatCompletion(self):
        try:
            response = openai.ChatCompletion.create(
                model=self.model_id,
                messages=self.messages,
                functions=self.functions,
                temperature=self.temperature,
                function_call={"name": "act"},
                request_timeout=5
            )
        except openai.error.InvalidRequestError:
            raise ValueError(self.name, self.messages)

        self.language_model_logs.append(response)

        usage = response["usage"]
        self.usage_statistics["total_tokens"] = usage["total_tokens"]

        if "function_call" in response.choices[0].message:
            name = response.choices[0].message["function_call"]["name"]
            parameters = json.loads(response.choices[0].message["function_call"]["arguments"])
            parameters["parameters"] = [parse_value(param) for param in parameters['parameters']]
            self.action_queue.append(parameters)
            self.working_memory.content = parameters["memory"]
        else:
            self.action_queue.append({"action": "Skip", "parameters": ["None"], "memory": "Skipped turn"})

        self.messages.append(response["choices"][0]["message"])

        return None

    def get_result(self):
        pass

    def set_up(self):

        action_names = ["Skip"]
        for key, action_list in self.action_space.items():
            for action in action_list:
                action_names.append(action.__name__)
        for key, query_list in self.query_space.items():
            for query in query_list:
                action_names.append(query.__name__)

        self.functions.append(
            {
                "name": "act",
                "description": "Make an action in the simulation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "The name of the action that you want to take.",
                            "enum":  action_names
                        },
                        "parameters": {
                            "type": "array",
                            "description": "The arguments for the action you want to take",
                            "items":
                                {
                                    "type": "string"
                                }
                        },
                        "memory": {
                            "type": "string",
                            "description": "your working memory",
                            "items":
                                {
                                    "type": "string"
                                }
                        }
                    },
                    "required": ["action", "parameters", "memory"]
                }

            }
        )

        self.add_message("system", self.system_prompt.get_prompt())

