import openai

from src.cxsim.agents.language_model_agents.language_model_agent import LanguageModelAgent
from cxsim.utilities.background_jobs.decorators import background_task
from src.cxsim.utilities.convert_string_to_json import string_to_dict
import json


class OAIAgent(LanguageModelAgent):
    def __init__(
            self,
            model_id: str = "gpt-3.5-turbo-0613"
    ):
        super(OAIAgent, self).__init__()
        self.model_id = model_id
        self.language_model_logs = []

        self.keep_last_n = 10

    def step(self):
        print("length of messages: ", len(self.messages))
        if len(self.messages) <= self.keep_last_n + 1:
            pass
        else:
            self.messages = [self.messages[0]] + self.messages[self.keep_last_n:]

    @background_task
    def execute_action(self):
        self.create_ChatCompletion()

        # In case of errors, you might want to return a default action or None
        return None

    @background_task
    def execute_query(self):
        self.create_ChatCompletion()

        return None

    @background_task
    def create_ChatCompletion(self):
        response = openai.ChatCompletion.create(
            model=self.model_id,
            messages=self.messages,
            functions = self.functions,
            temperature=self.temperature
        )
        print(self.name, response)
        self.add_message(response.choices[0].message.role, response.choices[0].message.content)

        self.language_model_logs.append(response)

        for message in self.messages:
            print(message)

        usage = response["usage"]
        self.usage_statistics["total_tokens"] = usage["total_tokens"]

        if "function_call" in response.choices[0].message:
            name = response.choices[0].message["function_call"]["name"]
            parameters = json.loads(response.choices[0].message["function_call"]["arguments"])

            if name == "do_action":
                self.action_queue.append(parameters)
            else:
                self.query_queue.append(parameters)

        if "content" in response.choices[0].message:
            self.working_memory.content = response.choices[0].message["content"]
        print(self.action_queue)
        print(self.query_queue)
        return None

    def get_result(self):
        pass

    def set_up(self):

        action_names = ["Skip"]
        for key, action_list in self.action_space.items():
            for action in action_list:
                action_names.append(action.__name__)

        query_names = ["Skip"]
        for key, query_list in self.query_space.items():
            for query in query_list:
                query_names.append(query.__name__)

        self.functions.append(
            {
                "name": "do_query",
                "description": "Allows you to make a Query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The name of the query you want to take.",
                            "enum": query_names
                        },
                        "parameters": {
                            "type": "array",
                            "description": "The arguments for the query you want to take",
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

        self.functions.append(
            {
                "name": "do_action",
                "description": "",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "The name of the action you want to take.",
                            "enum": action_names
                        },
                        "parameters":
                            {
                                "type": "array",
                                "description": "The arguments for the action you want to take, structure as a list of arguments",
                                "items":
                                    {
                                        "type": "string"
                                    }
                            }
                    },
                    "required": ["action", "parameters"]
                }
            },
        )
        self.add_message("system", self.system_prompt.content)
        self.create_ChatCompletion()

        self.action_queue.clear()
        self.query_queue.clear()
