from src.cxsim.agents.connnections.connection import Connection

from src.cxsim.prompts.prompt import PromptTemplate
import json
import asyncio
import re

import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
import requests


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
def completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)


class LanguageModelAPIConnection:
    def __init__(
            self,
            model_id: str = "gpt-3.5-turbo",
            backend: str = "openai",
            temperature: float = 0.55
    ):
        self.model_id = model_id
        self.backend = backend
        self.temperature = temperature

        self.messages = []
        self.full_messages = []
        self.message_length_checkpoints = []

        self.full_logs = []

        self.system_prompt = None
        self.prompt_order = []

        self.total_tokens = 0

        self.function_calls = []

        self.function_definitions = []

    def add_system_prompt(self, system_prompt: PromptTemplate, args):
        self.system_prompt = system_prompt

    def add_prompt(self, prompt: PromptTemplate, args):
        pass

    def turn(self):
        pass

    def complete(self, action_needed: bool, *args, **kwargs):
        response = completion_with_backoff(
            model=self.model_id,
            messages=self.messages,
            functions=self.function_definitions,
        )
        self.full_logs.append(response)
        self.total_tokens += response["usage"]["total_tokens"]
        if response.choices[0].message.get("function_call"):
            function_name = response.choices[0].message["function_call"]["name"]
            function_parameters = json.loads(response.choices[0].message["function_call"]["arguments"])
            self.function_calls.append({function_name: function_parameters})
        return response

    def compress_messages(self, n_steps: int = None, n_messages: int = None, keep_system: bool = True):
        if n_steps and n_messages:
            raise ValueError("Use either n_steps or n_messages, not both")
        self.messages.clear()
        if keep_system:
            self.messages.append(
                self.full_messages[0]
            )
        if n_messages:
            for message in self.full_messages[-n_messages:]:
                self.messages.append(message)
        elif n_steps:
            n_messages = len(self.full_messages) - self.message_length_checkpoints[-n_steps]
            for message in self.full_messages[-n_messages:]:
                self.messages.append(message)

    def add_message(self, role: str, content: str, function_name: str = None):
        """Add a message to the agents messaging dictionary"""
        if function_name:
            self.full_messages.append({"role": role, "name": function_name, "content": content})
            self.messages.append({"role": role, "name": function_name, "content": content})
        else:
            self.messages.append({"role": role, "content": content})
            self.full_messages.append({"role": role, "content": content})

