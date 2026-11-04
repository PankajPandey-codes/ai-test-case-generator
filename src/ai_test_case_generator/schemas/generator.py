from pydantic import BaseModel

from ai_test_case_generator.schemas.spec import ApiSpecDoc


class GeneratorInput(BaseModel):
    api_spec: ApiSpecDoc
    style_guide: str
    revision_feedback: str | None = None


class GeneratedTestCase(BaseModel):
    id: str
    name: str
    endpoint: str
    method: str
    category: str
    description: str


class GeneratorOutput(BaseModel):
    test_file_code: str
    test_cases: list[GeneratedTestCase]
    assumptions: list[str]
