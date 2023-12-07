import re
from typing import Union, List, Tuple, Dict, Any


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

    def set_variables(self, variables: Dict[str, str]):
        self.variables.update(variables)

    def __repr__(self):
        return self.get_content()


class PromptTemplate:
    def __init__(self, file_path: str = None, initial_data: str = None, section_headers: str = "[]", variable_indicators: str = "{}"):
        self.sections = {}
        self.variables = {}
        mid_idx_headers = len(section_headers) // 2
        mid_idx_indicators = len(variable_indicators) // 2
        self.section_open = section_headers[:mid_idx_headers]
        self.section_close = section_headers[mid_idx_headers:]
        self.variable_open = variable_indicators[:mid_idx_indicators]
        self.variable_close = variable_indicators[mid_idx_indicators:]

        self.content = ""

        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                initial_content = file.read()
        elif initial_data:
            initial_content = initial_data
        else:
            raise ValueError("Either 'file_path' or 'initial_data' must be provided.")

        self._parse_content(initial_content)

    def update_content(self):
        if not all(
                hasattr(section, 'get_content') and hasattr(section, 'priority') for section in self.sections.values()):
            self.content = "Invalid PromptSection objects"
            return

        sorted_sections = sorted(self.sections.values(),
                                 key=lambda x: (x.priority, list(self.sections.keys()).index(x.tag)))
        self.content = "\n\n".join([section.get_content() for section in sorted_sections])

    def sync_variables_to_sections(self):
        for section in self.sections.values():
            section.set_variables(self.variables)

    def _parse_content(self, content: str):
        section_splits = re.split(rf"({re.escape(self.section_open)}\s*.*?\s*{re.escape(self.section_close)})", content)
        for i in range(1, len(section_splits), 2):
            section_str = section_splits[i]
            tag_match = re.search(rf"{re.escape(self.section_open)}\s*(.*?)\s*{re.escape(self.section_close)}",
                                  section_str)
            if tag_match:
                tag = tag_match.group(1).strip()
            else:
                tag = None
            section_content = section_splits[i + 1].strip()

            # Extract variables within variable indicators
            variables = re.findall(rf"{re.escape(self.variable_open)}(.*?){re.escape(self.variable_close)}",
                                   section_content)
            for var in variables:
                self.variables[var] = None

            # Create a PromptSection object
            section = PromptSection(tag=tag, content=section_content)
            self.sections[tag or "default"] = section

    def add_section(self, section: PromptSection):
        """Add a new section or update an existing one."""
        if not isinstance(section, PromptSection):
            raise ValueError("The provided section must be an instance of the PromptSection class.")

        self.sections[section.tag] = section

    def remove_section(self, tag: str):
        self.sections.pop(tag, None)

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
        self.update_content()
        return self.content

    def __str__(self):
        return self.get_prompt()

    def __setitem__(self, key: str, value: str):
        self.set_variable(key, value)

    def __str__(self):
        return self.get_prompt()

    def get_sections(self):
        return list(self.sections.keys())

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
        self.sync_variables_to_sections()
        self.variables[var_name] = value
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

    def set_variables(self, variables: Dict[str, str]):
        for var_name, value in variables.items():
            self.set_variable(var_name, str(value))

    def set_artifact_descriptions(self, artifacts):
        formatted_descriptions = "\n".join([f"{idx}: {artifact.get_description()}"for idx, artifact in enumerate(artifacts)])
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

    def to_txt(self, filename: str):
        """
        Write the current content of the PromptTemplate to a text file.

        Args:
        filename (str): The name of the file to which the content will be written.
        """
        # Ensure content is up-to-date
        self.update_content()

        # Write the content to the specified file
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(self.content)
        except IOError as e:
            print(f"An error occurred while writing to file: {e}")

