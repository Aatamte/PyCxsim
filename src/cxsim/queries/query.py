from pydantic import BaseModel


def do_query(query: str, parameters: dict):
    return {"query": query, "parameters": parameters}


class Query(BaseModel):
    """"""
    query: str
    parameters: dict
