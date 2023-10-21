from dataclasses import fields
from typing import List, Any


def map_python_type_to_json(type_str: str) -> str:
    mapping = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
        "list": "array",
        "dict": "object",
        "Any": "any"
    }
    return mapping.get(type_str, "any")


class EnvironmentUtilities:
    def __init__(self):
        pass




    def get_artifact_descriptions(self, artifacts):
        formatted_descriptions = "\n".join([f"{idx}: {artifact.get_description()}"for idx, artifact in enumerate(artifacts)])
        return formatted_descriptions

    def format_openai_function_calls(self, functions: list) -> List[dict]:
        return [self.format_openai_function_call(func) for func in functions]

    def format_openai_function_call(self, dataclass_type: Any) -> dict:
        schema = {
            "name": dataclass_type.__name__.lower(),
            "description": dataclass_type.__doc__.strip() if dataclass_type.__doc__ else '',
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }

        for field_obj in fields(dataclass_type):
            type_name = field_obj.type.__name__ if hasattr(field_obj.type, '__name__') else str(field_obj.type)
            type_name = map_python_type_to_json(type_name)

            description = field_obj.metadata.get('description', '')

            schema["parameters"]["properties"][field_obj.name] = {
                "type": type_name,
                "description": description
            }

            if hasattr(field_obj.type, "__members__"):
                schema["parameters"]["properties"][field_obj.name]["enum"] = list(field_obj.type.__members__.keys())

            schema["parameters"]["required"].append(field_obj.name)

        return schema
