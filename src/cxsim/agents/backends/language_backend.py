from cxsim.prompts.prompt import PromptTemplate
from typing import Union
import json
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(2))
def completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)


class Local:
    def __init__(self):
        self.action_space = None

    @staticmethod
    def text_to_dict(text: str, delimiter: str, strict: bool = True):
        # Split the text by the delimiter
        parts = text.split(delimiter)

        # Ensure that there are at least two parts: an action and one parameter
        if strict and len(parts) < 2:
            raise ValueError("Text must contain an action and at least one parameter.")

        # The first part is the action
        action = parts[0].strip()

        # The remaining parts are parameters
        params = {}
        for part in parts[1:]:
            # Split each parameter into key and value
            if '=' in part:
                key, value = part.split('=', 1)
                params[key.strip()] = value.strip()
            elif strict:
                raise ValueError("All parameters must have a key and value.")
            else:
                params[part.strip()] = None

        return {"action": action, "params": params}

class OpenAI:
    def parse_function_call(self, response):
        func_call = None
        func_content = None

        if response.choices[0].message.get("function_call"):
            function_name = response.choices[0].message["function_call"]["name"]
            function_parameters = json.loads(response.choices[0].message["function_call"]["arguments"])
            func_call = {function_name: function_parameters}
        if response.choices[0].message.get("content"):
            func_content = response.choices[0].message["content"]

        return func_content, func_call

    def format_function_call(self, func_call):
        """
        formats a function call into a func(param_1 = _, param_2 = _) string
        Args:
            func_call:

        Returns:

        """
        func_call_dict = list(func_call.values())[
            0]  # Assuming func_call.values() returns a list with a dictionary as its first element
        formatted_args = ', '.join(f"{key}={repr(value)}" for key, value in func_call_dict.items())
        output = f"{list(func_call.keys())[0]}({formatted_args})"
        return output

    def complete(self, *args, **kwargs):
        pass


class LanguageBackend:
    def __init__(
            self,

            model_id: str = "gpt-3.5-turbo",
            service: str = "openai",
            temperature: float = 0.3,
            track_tokens: bool = False,
            exponential_backoff: bool = True
    ):
        self.model_id = model_id
        self.service = service
        self.temperature = temperature
        self.exponential_backoff = exponential_backoff

        self.messages = []
        self.full_messages = []
        self.message_length_checkpoints = []

        self.response_logs = []

        self.system_prompt = None
        self.prompt_order = []

        self.total_tokens = 0

        if self.service == "openai":
            pass
        elif self.service == "local":
            pass
        else:
            raise Warning("The only supported backend is openai or local")

        self.openai = OpenAI()

    def complete(self, *args, **kwargs):
        functions = kwargs.get('functions', [])
        messages = kwargs.pop('messages', self.messages)
        model_id = kwargs.pop('model_id', self.model_id)
        function_call = kwargs.pop('function_call', "auto")
        response = completion_with_backoff(
            model=model_id,
            messages=messages,
            function_call=function_call,
            functions=functions
        )
        self.response_logs.append(response)

        return response

    def compress_messages(self, n_steps_back: int = None, n_messages_back: int = None, keep_system: bool = True):
        if n_steps_back and n_messages_back:
            raise ValueError("Use either n_steps or n_messages, not both")

        self.messages.clear()

        if keep_system:
            if self.full_messages:  # Check if full_messages is not empty
                self.messages.append(self.full_messages[0])

        if n_messages_back:
            n_messages = min(n_messages_back, len(self.full_messages))  # Safeguard against index errors
            for message in self.full_messages[-n_messages:]:
                self.messages.append(message)
        elif n_steps_back:
            if self.message_length_checkpoints and n_steps_back <= len(
                    self.message_length_checkpoints):  # Check for valid index
                n_messages = len(self.full_messages) - self.message_length_checkpoints[-n_steps_back]
                n_messages = max(0, n_messages)  # Ensure n_messages is not negative
                for message in self.full_messages[-n_messages:]:
                    self.messages.append(message)

    def add_message(self, role: str, content: Union[str, PromptTemplate], function_name: str = None, override: bool = False):
        """Add a message to the agents messaging dictionary"""
        _content = None

        if not override:
            if isinstance(content, PromptTemplate):
                _content = content.get_prompt()
            elif isinstance(content, str):
                _content = content
            else:
                raise TypeError("content must be either a string or a PromptTemplate. You may set override = False to bypass this check")
        else:
            _content = content

        if function_name:
            self.full_messages.append({"role": role, "name": function_name, "content": _content})
            self.messages.append({"role": role, "name": function_name, "content": _content})
        else:
            self.messages.append({"role": role, "content": _content})
            self.full_messages.append({"role": role, "content": _content})

    def display(self):
        pass

