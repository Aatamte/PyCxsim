from dataclasses import dataclass
import importlib_resources
import copy
import inspect

# Open the file (replace 'your_package_name' with the actual name of your package)
with importlib_resources.open_text('src.caes.prompts', 'environment_system_prompt.txt') as file:
    system_prompt = file.read()

# Open the file (replace 'your_package_name' with the actual name of your package)
with importlib_resources.open_text('src.caes.prompts', 'observation_template_prompt.txt') as file:
    observation_prompt = file.read()


@dataclass
class Prompt:
    content: str

    def approximate_tokens(self):
        return len(self.content) * 4

    def calculate_tokens(self):
        return 0

    def merge(self, other):
        self.content += "\n"
        self.content += other.content


class ObservationPrompt:
    def __init__(self):
        self.content = observation_prompt
        self.artifact_information_list = []

    def set_inventory(self, inventory):
        self.content = self.content.replace("#!inventory!#", inventory)

    def set_current_step(self, current_step):
        self.content = self.content.replace("#!current_step!#", current_step)

    def set_artifact_information(self):
        artifact_information_string = ""
        for artifact_information in self.artifact_information_list:
            artifact_information_string += artifact_information + "\n"

        self.content = self.content.replace("#!artifact_information!#", artifact_information_string)

    def insert_artifact_information(self, artifact_information):
        self.artifact_information_list.append(artifact_information)


class SystemPrompt:
    def __init__(self):
        self.content = system_prompt

        self.artifact_descriptions = []
        self.global_actions = []

    def insert_artifact_description(self, prompt: Prompt):
        self.artifact_descriptions.append(prompt)

    def insert_global_action(self, action_string):
        self.global_actions.extend(action_string)

    def set_starting_inventory(self, inventory):
        self.content = self.content.replace("#!inventory!#", inventory)

    def set_action_restrictions(self, restrictions):
        restriction_string = ""
        for idx, (name, restriction_list) in enumerate(restrictions.items()):
            restriction_string += f"{name.__name__}: " + "[" + "\n"
            for rest in restriction_list:
                restriction_string += str(inspect.getsource(rest))
            restriction_string += "]"
        self.content = self.content.replace("#!action_restrictions!#", restriction_string)

    def set_num_artifacts(self, num_artifacts):
        self.content = self.content.replace("#!num_artifacts!#", num_artifacts)

    def set_artifact_descriptions(self):
        descriptions = ""
        for idx, artifact_description in enumerate(self.artifact_descriptions):
            descriptions += f"{idx + 1}: " + artifact_description + "\n"

        self.content = self.content.replace("#!artifact_descriptions!#", descriptions)

    def set_global_actions(self):
        global_action_string = ""
        for action in self.global_actions:
            global_action_string += str({"action": action, "reason": "<reason for action>"}) + "\n"

        self.content = self.content.replace("#!global_actions!#", global_action_string)

    def set_environment_information(self, num_agents, max_steps):
        self.content = self.content.replace("#!n_agents!#", num_agents)
        self.content = self.content.replace("#!max_steps!#", max_steps)

    def copy(self):
        return copy.deepcopy(self)

