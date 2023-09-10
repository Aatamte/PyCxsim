from pydantic import BaseModel
from typing import List


def do_query(query: str, parameters: List[str]):
    return {"query": query, "parameters": parameters}


class Query(BaseModel):
    """"""
    query: str
    parameters: List[str]
