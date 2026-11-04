from typing import Literal

from pydantic import BaseModel, Field

RubricDimension = Literal[
    "readability",
    "assertion_quality",
    "test_independence",
    "pytest_idioms",
    "maintainability",
]

RUBRIC_DIMENSIONS: tuple[RubricDimension, ...] = (
    "readability",
    "assertion_quality",
    "test_independence",
    "pytest_idioms",
    "maintainability",
)


class RubricScore(BaseModel):
    dimension: RubricDimension
    score: int = Field(ge=1, le=5)
    justification: str


class JudgeOutput(BaseModel):
    rubric_scores: list[RubricScore]
    rubric_average: float
    narrative: str
    verdict: Literal["pass", "fail"]
