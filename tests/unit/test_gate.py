from ai_test_case_generator.schemas.evidence import EvidenceReport, MutantResult
from ai_test_case_generator.schemas.judge import JudgeOutput, RubricScore
from evals.gate import compute_gate

GOOD_RUBRIC = JudgeOutput(
    rubric_scores=[RubricScore(dimension="readability", score=4, justification="ok")],
    rubric_average=4.0,
    narrative="Solid.",
    verdict="pass",
)

WEAK_RUBRIC = JudgeOutput(
    rubric_scores=[RubricScore(dimension="readability", score=2, justification="weak")],
    rubric_average=2.0,
    narrative="Weak.",
    verdict="fail",
)


def _evidence(baseline_passed: bool, kill_rate: float) -> EvidenceReport:
    return EvidenceReport(
        baseline_passed=baseline_passed,
        mutant_results=[MutantResult(bug_class="auth_bypass", killed=kill_rate > 0)],
        kill_rate=kill_rate,
    )


def test_gate_passes_when_all_three_thresholds_are_met():
    result = compute_gate(_evidence(True, 0.75), GOOD_RUBRIC)
    assert result.passed is True
    assert result.reasons == []


def test_gate_fails_on_low_kill_rate():
    result = compute_gate(_evidence(True, 0.5), GOOD_RUBRIC)
    assert result.passed is False
    assert any("kill_rate" in r for r in result.reasons)


def test_gate_fails_on_failed_baseline():
    result = compute_gate(_evidence(False, 0.9), GOOD_RUBRIC)
    assert result.passed is False
    assert any("baseline" in r for r in result.reasons)


def test_gate_fails_on_low_rubric_average():
    result = compute_gate(_evidence(True, 0.9), WEAK_RUBRIC)
    assert result.passed is False
    assert any("rubric_average" in r for r in result.reasons)


def test_gate_respects_custom_thresholds():
    result = compute_gate(_evidence(True, 0.6), GOOD_RUBRIC, kill_rate_min=0.5)
    assert result.passed is True
