from dataclasses import dataclass
import importlib_resources
import copy
import inspect
from dataclasses import fields
import re
from typing import Union, List, Tuple, Dict, Any


# Open the file (replace 'your_package_name' with the actual name of your package)
with importlib_resources.open_text('src.cxsim.prompts', 'system_prompt.txt') as file:
    system_prompt = file.read()

# Open the file (replace 'your_package_name' with the actual name of your package)
with importlib_resources.open_text('src.cxsim.prompts', 'observation_prompt.txt') as file:
    observation_prompt = file.read()

with importlib_resources.open_text('src.cxsim.prompts', 'state_of_mind_prompt.txt') as file:
    state_of_mind_prompt = file.read()


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

    def set_current_map(self, map_text):
        self.content = self.content.replace("#!current_map!#", map_text + "\nA: Other agents, O: You, .: empty spaces")

    def set_artifact_information(self):
        artifact_information_string = ""
        for artifact_information in self.artifact_information_list:
            artifact_information_string += artifact_information + "\n"

        self.content = self.content.replace("#!artifact_information!#", artifact_information_string)

    def insert_artifact_information(self, artifact_information):
        self.artifact_information_list.append(artifact_information)

    def set_working_memory(self, memory):
        self.content = self.content.replace("#!memory!#", memory)


class StateOfMindPrompt:
    def __init__(self):
        self.content = state_of_mind_prompt

    def insert_state_of_mind(self, state_of_mind):
        self.content = self.content.replace("#!state_of_mind!#", state_of_mind)


class PromptSection:
    def __init__(self, title: str = None,  tag: str = None, content: str = None, file_path: str = None,
                 include_header: bool = False, file_has_header: bool = True, priority: int = 1):
        self.tag = tag or ""   # A default empty string if no header provided
        self.title = title or ""
        self._content = content or "" # A default empty string if no content provided
        self.variables = {}
        self.include_header = include_header
        self.file_has_header = file_has_header
        self.priority = priority

        if file_path:
            self._load_from_file(file_path)
        else:
            self.set_content(self._content)

    def set_variable(self, var_name: str, value: str):
        """
        Set a variable's value. This variable can later be used in the section.

        :param var_name: Name of the variable.
        :param value: Value of the variable.
        """
        self.variables[var_name] = value

    def _load_from_file(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if content.startswith('[') and ']' in content and self.file_has_header:
                self.tag, content = content.split(']', 1)
                self.tag = self.tag.strip('[').strip()
            self.set_content(content)

    def get_content(self, use_tag: bool = False) -> str:
        """Retrieve the section content with variables replaced."""
        formatted_content = self._content.format(**self.variables)

        header = ""
        if self.include_header or use_tag:
            if self.tag:
                header += f"[{self.tag}]"
        if self.title:
            header += "\n" + self.title + "\n"

        return f"{header}{formatted_content}"

    def set_content(self, new_content: str):
        """Set the section content and extract variables."""
        self._content = new_content
        self._extract_variables_from_content()

    def _extract_variables_from_content(self):
        """Private method to extract all variable placeholders from content."""
        # Use regex to detect placeholders like {variable_name}
        variable_placeholders = re.findall(r"\{(.*?)\}", self._content)
        for var in variable_placeholders:
            if var not in self.variables:
                self.variables[var] = ""  # Default to an empty string for each extracted variable.

    def override_content(self, new_content: str):
        """Set or update the section content."""
        self.set_content(new_content)

    def get_variables_in_content(self) -> list:
        """Retrieve all variables/placeholders in the content."""
        return list(self.variables.keys())

    def format_list(self, items: list, delimiter: str = "\n", formatter_func: callable = None,
                    prefix: str = "", suffix: str = "", item_prefix: str = "", item_suffix: str = "") -> str:
        """
        Format a list of items into a string representation.

        :param items: List of items to format.
        :param delimiter: Delimiter to separate the items.
        :param formatter_func: Optional function to format each item.
        :param prefix: Text to prepend to the entire formatted list.
        :param suffix: Text to append to the entire formatted list.
        :param item_prefix: Text to prepend to each item in the list.
        :param item_suffix: Text to append to each item in the list.
        :return: Formatted string representation of the list.
        """
        if formatter_func:
            items = [formatter_func(item) for item in items]
        formatted_items = [f"{item_prefix}{item}{item_suffix}" for item in items]
        return prefix + delimiter.join(formatted_items) + suffix

    def format_dictionary(self, dictionary: dict, delimiter: str = "\n", formatter_func: callable = None,
                          prefix: str = "", suffix: str = "", item_prefix: str = "", item_suffix: str = "") -> str:
        """
        Format a dictionary into a string representation.

        :param dictionary: Dictionary to format.
        :param delimiter: Delimiter to separate key-value pairs.
        :param formatter_func: Optional function to format each key-value pair.
        :param prefix: Text to prepend to the entire formatted dictionary.
        :param suffix: Text to append to the entire formatted dictionary.
        :param item_prefix: Text to prepend to each key-value pair.
        :param item_suffix: Text to append to each key-value pair.
        :return: Formatted string representation of the dictionary.
        """
        formatted_items = []
        for key, value in dictionary.items():
            item_str = f"{key}: {value}"
            if formatter_func:
                item_str = formatter_func(key, value)
            formatted_items.append(f"{item_prefix}{item_str}{item_suffix}")
        return prefix + delimiter.join(formatted_items) + suffix

    def __repr__(self):
        return self.get_content()


class PromptTemplate:
    def __init__(self, file_path: str = None, initial_data: str = None):
        """
        Initialize the InitializationPrompt class.

        :param file_path: Path to the file from which to read the prompt.
        :param initial_data: Directly provide the starting prompt if not reading from a file.
        """
        self.sections = {}
        self.variables = {}
        if file_path:
            self.load_from_file(file_path)
        elif initial_data:
            self._parse_content(initial_data)
        else:
            raise ValueError("Either 'file_path' or 'initial_data' must be provided.")

    def add_section(self, section: PromptSection):
        """Add a new section or update an existing one."""
        if not isinstance(section, PromptSection):
            raise ValueError("The provided section must be an instance of the PromptSection class.")

        self.sections[section.tag] = section

    def load_from_file(self, file_path: str):
        """Load sections from a file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            sections = self.parse_sections_from_content(content)
            for tag, sec_content in sections:
                self.add_section(PromptSection(tag=tag, content=sec_content))

    def load_from_string(self, content: str):
        """Load sections directly from a string."""
        sections = self.parse_sections_from_content(content)
        for tag, sec_content in sections:
            self.add_section(PromptSection(tag=tag, content=sec_content))

    def remove_section(self, tag: str):
        """Remove a section by its tag."""
        if tag in self.sections:
            del self.sections[tag]

    def parse_sections_from_content(self, content: str) -> List[Tuple[str, str]]:
        """Parse sections from a string content."""

        section_contents = []
        current_header = None
        current_content = []

        for line in content.splitlines():
            if line.startswith('[') and ']' in line:
                if current_header and current_content:
                    section_contents.append((current_header, '\n'.join(current_content)))
                    current_content = []
                current_header = line.strip('[]').strip()
            else:
                current_content.append(line)

        # For the last section
        if current_header and current_content:
            section_contents.append((current_header, '\n'.join(current_content)))

        return section_contents

    def get_variables(self) -> Dict[str, Dict[str, str]]:
        """
        Get all variables from all sections.

        :return: A dictionary with section tags as keys and dictionaries of the section's variables as values.
        """
        return {section.tag: section.variables for section in self.sections.values()}

    def replace_section(self, tag: str, new_section: PromptSection):
        """
        Replace an existing section with a new one based on the provided tag.

        :param tag: The tag of the section to be replaced.
        :param new_section: The new PromptSection to replace the existing one.
        """
        # Remove the old section if it exists
        self.sections = {k: v for k, v in self.sections.items() if v.tag != tag}
        # Add the new section
        self.add_section(new_section)

    def get_section(self, tag: str) -> PromptSection:
        """Retrieve a section by its tag."""
        return self.sections.get(tag, None)

    def get_prompt(self) -> str:
        """Compile and retrieve the entire prompt."""
        # Sorting sections by their priority and then by their order of addition
        sorted_sections = sorted(self.sections.values(),
                                 key=lambda x: (x.priority, list(self.sections.keys()).index(x.tag)))
        return "\n\n".join([section.get_content() for section in sorted_sections])

    def __str__(self):
        return self.get_prompt()

    def get_sections(self):
        return list(self.sections.keys())

    def _parse_content(self, content: str):
        for section_str in content.strip().split("\n\n"):
            # Check if section starts with a header format
            if section_str.startswith('[') and ']' in section_str:
                tag, section_content = section_str.split(']', 1)
                tag = tag.strip('[').strip()
            else:
                tag = None
                section_content = section_str

            # Extract title and content
            lines = section_content.strip().split("\n", 1)
            title = lines[0] if len(lines) > 1 else None
            actual_content = lines[1] if len(lines) > 1 else lines[0]

            # Create a PromptSection object
            section = PromptSection(title=title, tag=tag, content=actual_content)
            self.sections[tag or "default"] = section

    def set_variable(self, var_name: str, value: str, section_tag: str = None):
        """
        Set a variable's value for a specific section. This variable can later be used in the section.

        :param var_name: Name of the variable.
        :param value: Value of the variable.
        :param section_tag: (Optional) Tag of the section where the variable is to be set.
                            If not provided, the variable is set in every section that contains it.
        """
        # Ensure case-insensitive look-up by using lowercase versions of section tags
        sections_lower = {key.lower(): value for key, value in self.sections.items()}

        if section_tag:
            section_tag = section_tag.lower()  # Convert to lowercase for case-insensitivity
            section = sections_lower.get(section_tag)

            if section:
                section.set_variable(var_name, value)
            else:
                raise ValueError(f"No section with tag '{section_tag}' exists.")

        else:
            for section in self.sections.values():
                # Using lower() for case-insensitive match in content
                if var_name.lower() in section.get_content().lower():
                    section.set_variable(var_name, value)

    def format_artifact_description(self, artifact):
        description = f"{artifact.name}\n"

        description += "ACTIONS:\n"
        for action in artifact.get_action_space():
            action_name = str(action.__name__)
            action_parameters = [f"{field.name} {field.type}" for field in fields(action)]
            description += f"act(action={action_name}, parameters={action_parameters}, memory=<your memory>)\n"
            description += f"action information: {action.__doc__}"

        description += "\nQUERIES:\n"
        for query in artifact.get_query_space():
            query_name = str(query.__name__)
            query_parameters = [f"{field.name} {field.type}" for field in fields(query)]
            description += f"act(action={query_name}, parameters={query_parameters}, memory=<your memory>)\n"

        return description

    def set_artifact_descriptions(self, artifacts):
        formatted_descriptions = "\n".join([self.format_artifact_description(artifact) for artifact in artifacts])
        print(formatted_descriptions)
        self.set_variable("artifact_descriptions", formatted_descriptions, "Artifact Information")

    def format_list(self, items: list, delimiter: str = "\n", formatter_func: callable = None,
                    prefix: str = "", suffix: str = "", item_prefix: str = "", item_suffix: str = "") -> str:
        """
        Format a list of items into a string representation.

        :param items: List of items to format.
        :param delimiter: Delimiter to separate the items.
        :param formatter_func: Optional function to format each item.
        :param prefix: Text to prepend to the entire formatted list.
        :param suffix: Text to append to the entire formatted list.
        :param item_prefix: Text to prepend to each item in the list.
        :param item_suffix: Text to append to each item in the list.
        :return: Formatted string representation of the list.
        """
        if formatter_func:
            items = [formatter_func(item) for item in items]
        formatted_items = [f"{item_prefix}{item}{item_suffix}" for item in items]
        return prefix + delimiter.join(formatted_items) + suffix

    def format_dictionary(self, dictionary: dict, delimiter: str = "\n", formatter_func: callable = None,
                          prefix: str = "", suffix: str = "", item_prefix: str = "", item_suffix: str = "") -> str:
        """
        Format a dictionary into a string representation.

        :param dictionary: Dictionary to format.
        :param delimiter: Delimiter to separate key-value pairs.
        :param formatter_func: Optional function to format each key-value pair.
        :param prefix: Text to prepend to the entire formatted dictionary.
        :param suffix: Text to append to the entire formatted dictionary.
        :param item_prefix: Text to prepend to each key-value pair.
        :param item_suffix: Text to append to each key-value pair.
        :return: Formatted string representation of the dictionary.
        """
        formatted_items = []
        for key, value in dictionary.items():
            item_str = f"{key}: {value}"
            if formatter_func:
                item_str = formatter_func(key, value)
            formatted_items.append(f"{item_prefix}{item_str}{item_suffix}")
        return prefix + delimiter.join(formatted_items) + suffix


class ContextualPrompt(PromptTemplate):
    def __init__(self, file_path: str = None, initial_data: str = None):
        """
        Initialize the ContextualPrompt class.
        :param file_path: Path to the file from which to read the prompt.
        :param initial_data: Directly provide the starting prompt if not reading from a file.
        """
        super().__init__(file_path=file_path, initial_data=initial_data)

    def update_state(self, state_dict: Dict[str, Any]):
        """
        Update the state of the ContextualPrompt using a dictionary.
        The dictionary will be used to set variables across all sections.

        :param state_dict: Dictionary containing state variables to update.
        """
        for section in self.sections.values():
            for key, value in state_dict.items():
                section.set_variable(key, value)


class InitializationPrompt(PromptTemplate):
    def __init__(self, file_path: str = None, initial_data: str = None):
        """
        Initialize the ContextualPrompt class.
        :param file_path: Path to the file from which to read the prompt.
        :param initial_data: Directly provide the starting prompt if not reading from a file.
        """
        super().__init__(file_path=file_path, initial_data=initial_data)


class SystemPrompt:
    def __init__(self):
        self.content = system_prompt

        self.query_space = None
        self.action_space = None

        self.artifact_descriptions = {}
        self.global_actions = []
        self.artifacts = []

    def insert_artifact(self, artifact):
        self.artifacts.append(artifact)

    def insert_global_action(self, action_string):
        self.global_actions.extend(action_string)

    def set_starting_inventory(self, inventory):
        self.content = self.content.replace("#!inventory!#", inventory)

    def set_name(self, name):
        self.content = self.content.replace("#!agent_name!#", name)

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
        for idx, artifact in enumerate(self.artifacts):
            descriptions += f"{idx + 1}: " + artifact.name + "\n" + artifact.system_prompt.content \
                + "\n"
            descriptions += "ACTIONS:" + "\n"
            for action in artifact.get_action_space():
                action_name = str(action.__name__)
                action_parameters = [f"{field.name} {field.type}" for field in fields(action)]

                descriptions += "act(action=" + str(action_name) + ", parameters=" + str(action_parameters) + ", memory=<your memory>)" +  "\n"
            descriptions += "QUERIES:" + "\n"
            for query in artifact.get_query_space():
                query_name = str(query.__name__)
                query_parameters = [f"{field.name} {field.type}" for field in fields(query)]
                descriptions += "act(action=" + str(query_name) + ", parameters=" + str(query_parameters) + ", memory=<your memory>)" + "\n"

        self.content = self.content.replace("#!artifact_descriptions!#", descriptions)

    def set_global_actions(self):
        global_action_string = ""
        for action in self.global_actions:
            global_action_string += str({"action": action, "reason": "<reason for action>"}) + "\n"

        #self.content = self.content.replace("#!global_actions!#", global_action_string)

    def set_environment_information(self, num_agents, max_steps):
        self.content = self.content.replace("#!n_agents!#", num_agents)
        self.content = self.content.replace("#!max_steps!#", max_steps)

    def copy(self):
        return copy.copy(self)


