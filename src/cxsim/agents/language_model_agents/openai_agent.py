import openai

from src.cxsim.agents.language_model_agents.language_model_agent import LanguageModelAgent
from cxsim.utilities.background_jobs.decorators import background_task
from src.cxsim.utilities.convert_string_to_json import string_to_dict


class OAIAgent(LanguageModelAgent):
    def __init__(
            self,
            model_id: str = "gpt-3.5-turbo-0613"
    ):
        super(OAIAgent, self).__init__()
        self.model_id = model_id
        self.language_model_logs = []

        self.action_queue = []
        self.query_queue = []
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
        print(self.messages)

        # In case of errors, you might want to return a default action or None
        return None

    @background_task
    def execute_query(self):
        self.create_ChatCompletion(False)

        return None

    def create_ChatCompletion(self, action: bool = True):
        try:
            response = openai.ChatCompletion.create(
            model=self.model_id,
            messages=self.messages,
            functions = self.functions,
            temperature=self.temperature
            )
            print(response)
        except openai.error.InvalidRequestError as e:
            print(e.json_body)
            print(e.http_status)
            print(e.request_id)

        self.messages.append(
            {'role': response.choices[0].message.role, 'content': response.choices[0].message.content}
        )
        usage = response["usage"]
        self.usage_statistics["total_tokens"] = usage["total_tokens"]
        try:
            # Get the last message's content
            response = self.messages[-1]["content"]

            # Process the response to get action_string
            response_string = response.strip("\n").split("\n")[0]
            response_dict = string_to_dict(response_string)

            self.working_memory.content = response_dict["working_memory"]

            if action:
                # Append the action to the action queue
                self.action_queue.append(response_dict)
            else:
                self.query_queue.append(response_dict)

            return response_dict

        except (ValueError, SyntaxError, TypeError):
            # This will catch errors from ast.literal_eval and any type issues
            # Handle or log the error here if necessary
            pass

        # In case of errors, you might want to return a default action or None
        return None

    def get_result(self):
        pass

    def set_up(self):
        self.add_message("system", self.system_prompt.content)
        self.create_ChatCompletion(True)
        try:
            self.action_queue.pop(0)
        except:
            pass
