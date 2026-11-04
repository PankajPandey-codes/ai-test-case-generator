from ai_test_case_generator.schemas.evidence import EvidenceReport, GateResult
from ai_test_case_generator.schemas.judge import JudgeOutput


def compute_gate(
    evidence: EvidenceReport,
    judge_output: JudgeOutput,
    kill_rate_min: float = 0.70,
    rubric_min: float = 3.5,
) -> GateResult:
    """The binding pass/fail decision — plain Python, never an LLM opinion.

    passed = baseline_passed AND kill_rate >= kill_rate_min AND rubric_average >= rubric_min
    """
    reasons = []
    if not evidence.baseline_passed:
        reasons.append("baseline run did not pass 100% green")
    if evidence.kill_rate < kill_rate_min:
        reasons.append(f"kill_rate {evidence.kill_rate:.2f} below minimum {kill_rate_min:.2f}")
    if judge_output.rubric_average < rubric_min:
        reasons.append(f"rubric_average {judge_output.rubric_average:.2f} below minimum {rubric_min:.2f}")

    return GateResult(
        passed=len(reasons) == 0,
        kill_rate=evidence.kill_rate,
        rubric_average=judge_output.rubric_average,
        reasons=reasons,
    )
