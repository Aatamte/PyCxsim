import re


def parse_output(text):
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