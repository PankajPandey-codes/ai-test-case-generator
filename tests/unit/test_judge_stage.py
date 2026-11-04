from ai_test_case_generator.pipeline.judge import judge
from ai_test_case_generator.schemas.critic import CritiqueReport
from ai_test_case_generator.schemas.evidence import EvidenceReport, MutantResult
from ai_test_case_generator.schemas.generator import GeneratedTestCase, GeneratorOutput
from ai_test_case_generator.schemas.judge import JudgeOutput, RubricScore
from tests.fixtures.fake_llm_client import FakeLLMClient

GEN_OUTPUT = GeneratorOutput(
    test_file_code="def test_x():\n    assert True\n",
    test_cases=[
        GeneratedTestCase(
            id="tc-1", name="test_x", endpoint="/applicants", method="POST",
            category="validation", description="Checks validation.",
        )
    ],
    assumptions=[],
)

CRITIQUE = CritiqueReport(syntax_valid=True, coverage_gaps=[], code_issues=[], overall_recommendation="accept")

EVIDENCE = EvidenceReport(
    baseline_passed=True,
    mutant_results=[MutantResult(bug_class="auth_bypass", killed=True, failing_test_ids=["t::x"])],
    kill_rate=5 / 7,
)

# LLM reports scores that average to 4.0, but deliberately claims a wrong
# rubric_average (3.0) to prove judge() recomputes it rather than trusting it.
LLM_OUTPUT_WITH_WRONG_AVERAGE = JudgeOutput(
    rubric_scores=[
        RubricScore(dimension="readability", score=5, justification="clear"),
        RubricScore(dimension="assertion_quality", score=4, justification="good"),
        RubricScore(dimension="test_independence", score=4, justification="good"),
        RubricScore(dimension="pytest_idioms", score=3, justification="ok"),
        RubricScore(dimension="maintainability", score=4, justification="good"),
    ],
    rubric_average=3.0,
    narrative="Decent suite.",
    verdict="pass",
)


def test_judge_recomputes_rubric_average_from_scores():
    fake = FakeLLMClient({JudgeOutput: [LLM_OUTPUT_WITH_WRONG_AVERAGE]})
    result = judge(fake, GEN_OUTPUT, CRITIQUE, EVIDENCE)

    assert result.rubric_average == 4.0
    assert result.rubric_average != 3.0
