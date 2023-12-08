from typing import Union, List
from cxsim.prompts.prompt import PromptTemplate


class TextIO:
    def __init__(self, agent):
        self.agent = agent
        self.format = ChatFormat()
        self.prompts = {}
        self.variables = {}

        # config variables
        self.use_agent_variables = False

    def add_prompt(self, name: str, prompt: PromptTemplate):
        """
        Add a PromptTemplate to the prompts dictionary and extract its variables.
        """
        self.prompts[name] = prompt

    def add_message(self, role: str, content: Union[str, PromptTemplate], function_name: str = None, override: bool = False):
        return self.format.add_message(role=role, content=content, function_name=function_name, override=override)

    def process_text_input(self, text: str, delimiter: str = " ", strict: bool = True) -> dict:
        """
        Process a text input and return a structured dictionary with action and parameters.
        """
        # Split the text by the delimiter
        parts = text.split(delimiter)

        # Validate and process the text input
        if strict and len(parts) < 2:
            raise ValueError("Text must contain an action and at least one parameter.")
        action = parts[0].strip()
        params = {part.split('=')[0].strip(): part.split('=')[1].strip() for part in parts[1:] if '=' in part}

        return {"action": action, "params": params}

    def format_text_response(self, response: dict) -> str:
        """
        Format a dictionary response into a string representation.
        """
        formatted_response = response["action"]
        if response.get("params"):
            formatted_params = ', '.join(f"{key}={repr(value)}" for key, value in response["params"].items())
            formatted_response += f"({formatted_params})"
        return formatted_response

    def get_updated_prompt(self, prompt_name: str):
        # Retrieve the current variables from the prompt

        # Update the variables from the agent's variable registry
        updated_variables = {}
        for key, value in self.agent.variable_registry.items():
            # Check if the value is a callable (e.g., a function or lambda), and call it if so
            updated_variables[key] = value() if callable(value) else value

        # Set the updated variables to the prompt
        self.prompts[prompt_name].set_variables(updated_variables)

        return self.prompts[prompt_name]

    @property
    def messages(self):
        return self.format.messages

    @property
    def full_messages(self):
        return self.format.full_messages

class ChatFormat:
    def __init__(self):
        self.messages = []
        self.full_messages = []
        self.message_length_checkpoints = []

    def add_message(self, role: str, content: Union[str, PromptTemplate], function_name: str = None, override: bool = False):
        """Add a message to the agents messaging dictionary"""
        _content = None

        if not override:
            if isinstance(content, PromptTemplate):
                _content = str(content)
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
