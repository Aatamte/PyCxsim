import openai
from cxsim.agents.language_model_agents.language_model_agent import LanguageModelAgent
import json
import re

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)


def parse_value(val):
    if not isinstance(val, str):  # Ensure val is a string
        return val

    if re.match(r'^-?\d+$', val):  # Checks if the string is a whole number (positive or negative)
        return int(val)

    # You can add more regex checks here for other numerical types, e.g., floats
    return val


class OpenAIAgent(LanguageModelAgent):
    def __init__(self, model_id: str = "gpt-3.5-turbo"):
        super(OpenAIAgent, self).__init__()
        self.model_id = model_id
        self.language_model_logs = []
        self.temperature = 0.55

        self.keep_last_n = 2
        self.current_message_length = 0
        self.enable_reflect = False

    def decide(self):
        try:
            response = self.connection.send(
                model=self.model_id,
                messages=self.messages,
                functions=self.functions,
                temperature=self.temperature,
                function_call={"name": "act"}
            )

        except openai.error.InvalidRequestError as e:
            print(e)
            raise ValueError(self.name, self.messages)

        if "function_call" in response.choices[0].message:
            name = response.choices[0].message["function_call"]["name"]
            parameters = json.loads(response.choices[0].message["function_call"]["arguments"])
            parameters["parameters"] = [parse_value(param) for param in parameters['parameters']]
            self.action_queue.append(parameters)
        else:
            self.action_queue.append({"action": "Skip", "parameters": ["None"]})

        self.messages.append(response["choices"][0]["message"])

        return None

    def reflect(self):
        try:
            response = completion_with_backoff(
                model=self.model_id,
                messages=self.messages,
                # functions=self.functions,
                temperature=self.temperature,
                request_timeout=30
            )
        except openai.error.InvalidRequestError:
            raise ValueError(self.name, self.messages)

        self.language_model_logs.append(response)

        self.add_message("assistant", response["choices"][0]["message"]["content"])
        return None
