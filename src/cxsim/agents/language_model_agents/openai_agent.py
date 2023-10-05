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


class OpenAIAgent(LanguageModelAgent):
    def __init__(self, model_id: str = "gpt-3.5-turbo"):
        super(OpenAIAgent, self).__init__()
        self.model_id = model_id
        self.language_model_logs = []
        self.temperature = 0.55

        self.keep_last_n = 2
        self.current_message_length = 0

    def step(self):
        index_to_keep = None
        #print(self.messages)
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

        self.inbox.clear()

    def set_decision_prompt(self, environment):
        self.decision_prompt.set_variable("inventory", str(self.display_inventory()), "decision prompt")
        self.decision_prompt.set_variable("inbox", str(self.inbox), "decision prompt")
        self.decision_prompt.set_variable("current_step", environment.current_step, "decision prompt")
        self.decision_prompt.set_variable("max_steps", environment.max_steps, "decision prompt")
        self.add_message("user", self.decision_prompt.get_prompt())

    def set_cognitive_prompt(self, environment, observation):
        # do cognitive step
        if len(self.action_history) >= 1:
            action_history = self.action_history[-1]
        else:
            action_history = self.action_history
        self.cognitive_prompt.set_variable("goal", self.goal, "cognitive prompt")
        self.cognitive_prompt.set_variable("action_history", str(action_history), "cognitive prompt")
        self.cognitive_prompt.set_variable("action_result", observation, "cognitive prompt")
        if self.params:
            self.cognitive_prompt.set_variable("params", self.params, "cognitive prompt")
        self.add_message("user", self.cognitive_prompt.get_prompt())

    def decide(self):
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

    def reflect(self):
        try:
            response = openai.ChatCompletion.create(
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

    def set_system_prompt(self, environment):
        # Setting variables for the agent's prompt sections
        self.system_prompt.set_variable("name", self.name, "Agent information")

        # Inventory
        self.system_prompt.set_variable("inventory", str(self.inventory.starting_inventory), "Agent information")
        self.system_prompt.set_variable("goal", str(self.params["goal"]), "Agent information")

        # Action Restrictions
        formatted_action_restrictions = self.system_prompt.sections["Action Restrictions"].format_list(
            self.action_restrictions)
        self.system_prompt.set_variable("action_restrictions", formatted_action_restrictions, "Action Restrictions")

        # Environment Information
        self.system_prompt.set_variable("n_agents", str(len(environment.agents)), "Environment information")
        self.system_prompt.set_variable("max_steps", str(environment.max_steps), "Environment information")
        self.system_prompt.set_variable("agent_names", str(environment.agent_names), "Environment information")


        # Artifacts
        num_artifacts = len(environment.action_handler.artifacts)
        self.system_prompt.set_variable("num_artifacts", str(num_artifacts), "Artifact information")
        self.system_prompt.set_artifact_descriptions(environment.artifacts)

        # Assuming global actions are a list
        formatted_global_actions = self.system_prompt.format_list(["""act(action="Skip", parameters=["None"])"""])
        self.system_prompt.set_variable("global_actions", formatted_global_actions, "Action space")

        self.system_prompt.set_variable("current_position", str((self.x_pos, self.y_pos)))

        self.system_prompt.remove_section("Action Restrictions")
        self.system_prompt.remove_section("Action Space")

    def prepare(self):
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

