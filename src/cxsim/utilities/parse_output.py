import re


class TextParsing:
    def __init__(self):
        pass

    def parse_output(self, text):
        """
        Parses a given text with <|tag|> headers and returns a list of dictionaries,
        each containing the header as 'role' and the associated content.

        Args:
        text (str): The text to be parsed.

        Returns:
        list of dict: A list of dictionaries with 'role' and 'content' keys.
        """

        try:
            # Regular expression pattern to match <|tag|> and capture the text until the start of the next <|tag|> or end of string
            pattern = r'<\|(.*?)\|>(.*?)(?=<\||\Z)'

            # Find all matches in the text
            matches = re.findall(pattern, text, re.DOTALL)

            # Return a list of dictionaries for each match
            return [{'role': header.strip(), 'content': content.strip()} for header, content in matches]

        except Exception as e:
            # Log the exception for debugging
            print(f"An error occurred: {e}")
            # Return an empty list in case of error
            return []


    def parse_text_to_json(self, text):
        # Regular expression pattern to match the entire <Action> block
        action_block_pattern = r"<Action>\s*(.*?)\s*</Action>"

        # Regular expression pattern to match action and parameters within the <Action> block
        action_pattern = r"(\w+)\((.*?)\)"

        # Find the <Action> block in the text
        action_block_match = re.search(action_block_pattern, text, re.DOTALL)
        if not action_block_match:
            return "No valid action block found in the text"

        action_block = action_block_match.group(1)

        # Find action and parameters within the <Action> block
        action_match = re.search(action_pattern, action_block)
        if not action_match:
            return "No valid action found in the action block"

        action = action_match.group(1)
        params = action_match.group(2).split(',')

        # Process parameters to handle different types (integers, strings)
        processed_params = {}
        for i, param in enumerate(params, start=1):
            param = param.strip()
            try:
                # Attempt to convert to integer
                processed_param = int(param)
            except ValueError:
                # If conversion fails, treat as a string (remove surrounding quotes)
                processed_param = param.strip('\'\"')

            # Use default parameter names if specific names are not provided
            param_key = f"param{i}"
            processed_params[param_key] = processed_param

        return {action: processed_params}