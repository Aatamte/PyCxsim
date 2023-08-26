import ast
import json
import re


def string_to_dict(s: str) -> dict:
    s = s.strip()

    try:
        return ast.literal_eval(s)
    except Exception:
        pass

    try:
        return json.loads(s.replace("'", '"'))
    except Exception:
        pass

    # Improved regex pattern
    pattern = r"['\"]?(\w+)['\"]?\s*:\s*['\"]?([^,'\"{}]+)['\"]?"
    matches = re.findall(pattern, s)
    result = {match[0]: match[1] for match in matches}

    # If we couldn't extract any key-value pairs, raise ValueError
    if not result:
        raise ValueError(f"Unable to parse string as dictionary: {s}")

    return result
