from pydantic import BaseModel


class MutantResult(BaseModel):
    bug_class: str
    killed: bool
    failing_test_ids: list[str] = []


class EvidenceReport(BaseModel):
    baseline_passed: bool
    mutant_results: list[MutantResult]
    kill_rate: float


class GateResult(BaseModel):
    passed: bool
    kill_rate: float
    rubric_average: float
    reasons: list[str]
