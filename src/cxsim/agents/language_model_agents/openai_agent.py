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
    def __init__(self, model_id: str = "gpt-3.5-turbo"):
        super(OAIAgent, self).__init__()
        self.model_id = model_id
        self.language_model_logs = []
        self.temperature = 0.35

        self.keep_last_n = 8
        self.current_message_length = 0

    def step(self):
        index_to_keep = None

        # Iterate backward through the messages
        n_back = 0
        for i in range(len(self.messages) - 1, -1, -1):
            if self.messages[i]["content"] is not None:
                if self.messages[i]["content"].startswith("CURRENT STEP"):
                    index_to_keep = i
                    n_back += 1
                    if n_back >= 3:
                        break

        # If the message is found, keep only the messages from that point onward
        if index_to_keep is not None:
            self.messages = [self.messages[0]] + self.messages[index_to_keep:]
        # Else, if the message is not found, you can keep the logic you already have
        elif len(self.messages) > self.keep_last_n + 1:
            self.messages = [self.messages[0]] + self.messages[-self.keep_last_n:]

    def decide(self):
        self.create_ChatCompletion()
        return None

    def reflect(self):
        self.reflection_completion()
        return None

    def execute_query(self):
        self.reflection_completion()
        return None

    def reflection_completion(self):
        try:
            response = openai.ChatCompletion.create(
                model=self.model_id,
                messages=self.messages,
                #functions=self.functions,
                temperature=self.temperature,
                request_timeout=30
            )
        except openai.error.InvalidRequestError:
            raise ValueError(self.name, self.messages)

        self.language_model_logs.append(response)

        self.add_message("assistant", response["choices"][0]["message"]["content"])

    def create_ChatCompletion(self):
        try:
            response = openai.ChatCompletion.create(
                model=self.model_id,
                messages=self.messages,
                functions=self.functions,
                temperature=self.temperature,
                function_call={"name": "act"},
                request_timeout=30
            )

        except openai.error.InvalidRequestError as e:
            print(e)
            raise ValueError(self.name, self.messages)

        self.language_model_logs.append(response)

        usage = response["usage"]
        self.usage_statistics["total_tokens"] = usage["total_tokens"]

        if "function_call" in response.choices[0].message:
            name = response.choices[0].message["function_call"]["name"]
            parameters = json.loads(response.choices[0].message["function_call"]["arguments"])
            parameters["parameters"] = [parse_value(param) for param in parameters['parameters']]
            self.action_queue.append(parameters)
        else:
            self.action_queue.append({"action": "Skip", "parameters": ["None"]})

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
                        }
                    },
                    "required": ["action", "parameters"]
                }

            }
        )

        self.add_message("system", self.system_prompt.get_prompt())

