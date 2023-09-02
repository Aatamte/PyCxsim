import openai

from src.caes.agents.language_model_agents.language_model_agent import LanguageModelAgent
from src.caes.background_jobs.decorators import background_task
from src.caes.utilities.convert_string_to_json import string_to_dict


class OAIAgent(LanguageModelAgent):
    def __init__(
            self,
            model_id: str = "gpt-3.5-turbo-0613"
    ):
        super(OAIAgent, self).__init__()
        self.model_id = model_id
        self.language_model_logs = []

        self.action_queue = []

    @background_task
    def execute_action(self):
        self.create_ChatCompletion()

        try:
            # Get the last message's content
            response = self.messages[-1]["content"]

            # Process the response to get action_string
            action_string = response.strip("\n").split("\n")[0]
            action_dict = string_to_dict(action_string)

            # Append the action to the action queue
            self.action_queue.append(action_dict)
            return action_dict

        except (ValueError, SyntaxError, TypeError):
            # This will catch errors from ast.literal_eval and any type issues
            # Handle or log the error here if necessary
            pass

        # In case of errors, you might want to return a default action or None
        return None

    def create_ChatCompletion(self):
        response = openai.ChatCompletion.create(
            model=self.model_id,
            messages=self.messages,
            temperature=self.temperature
        )

        self.messages.append(
            {'role': response.choices[0].message.role, 'content': response.choices[0].message.content}
        )
        usage = response["usage"]
        self.usage_statistics["total_tokens"] = usage["total_tokens"]

    def get_result(self):
        pass

    def set_up(self):
        self.messages.append(
            {
                "role": "system",
                "content": self.system_prompt.content
            }
        )
        self.create_ChatCompletion()
