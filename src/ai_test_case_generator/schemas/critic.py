from typing import Literal

from pydantic import BaseModel


class CoverageGap(BaseModel):
    endpoint: str
    category: str
    description: str


class CodeIssue(BaseModel):
    description: str
    severity: Literal["low", "medium", "high"]
    line_hint: int | None = None


class CritiqueReport(BaseModel):
    syntax_valid: bool
    coverage_gaps: list[CoverageGap]
    code_issues: list[CodeIssue]
    overall_recommendation: Literal["accept", "revise"]
