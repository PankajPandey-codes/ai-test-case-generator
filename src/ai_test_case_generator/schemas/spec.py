from pydantic import BaseModel


class EndpointSpec(BaseModel):
    path: str
    method: str
    description: str
    categories: list[str]


class ApiSpecDoc(BaseModel):
    title: str
    version: str
    endpoints: list[EndpointSpec]
