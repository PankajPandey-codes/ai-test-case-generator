from ai_test_case_generator.pipeline.orchestrator import run_pipeline
from ai_test_case_generator.schemas.critic import CritiqueReport
from ai_test_case_generator.schemas.evidence import EvidenceReport, MutantResult
from ai_test_case_generator.schemas.generator import GeneratedTestCase, GeneratorOutput
from ai_test_case_generator.schemas.judge import JudgeOutput, RubricScore
from tests.fixtures.fake_llm_client import FakeLLMClient
from tests.fixtures.sample_spec import build_sample_spec

CASE = GeneratedTestCase(
    id="tc-1", name="test_x", endpoint="/applicants", method="POST",
    category="validation", description="Checks validation.",
)
GEN_OUTPUT = GeneratorOutput(test_file_code="def test_x():\n    assert True\n", test_cases=[CASE], assumptions=[])

CRITIQUE_REVISE = CritiqueReport(syntax_valid=True, coverage_gaps=[], code_issues=[], overall_recommendation="revise")
CRITIQUE_ACCEPT = CritiqueReport(syntax_valid=True, coverage_gaps=[], code_issues=[], overall_recommendation="accept")

JUDGE_OUTPUT = JudgeOutput(
    rubric_scores=[RubricScore(dimension="readability", score=4, justification="ok")],
    rubric_average=4.0,
    narrative="ok",
    verdict="pass",
)

EVIDENCE = EvidenceReport(
    baseline_passed=True,
    mutant_results=[MutantResult(bug_class="auth_bypass", killed=True, failing_test_ids=["t::x"])],
    kill_rate=5 / 7,
)


class FakeHarness:
    def __init__(self):
        self.calls = 0

    def evaluate(self, gen_output):
        self.calls += 1
        return EVIDENCE


def test_revision_loop_runs_generator_and_critic_exactly_twice_when_critic_says_revise():
    fake_llm = FakeLLMClient(
        {
            GeneratorOutput: [GEN_OUTPUT, GEN_OUTPUT],
            CritiqueReport: [CRITIQUE_REVISE, CRITIQUE_ACCEPT],
            JudgeOutput: [JUDGE_OUTPUT],
        }
    )
    harness = FakeHarness()

    result = run_pipeline(build_sample_spec(), fake_llm, harness)

    generator_calls = sum(1 for c in fake_llm.calls if c["output_format"] is GeneratorOutput)
    critic_calls = sum(1 for c in fake_llm.calls if c["output_format"] is CritiqueReport)
    assert generator_calls == 2
    assert critic_calls == 2
    assert harness.calls == 1
    assert result.critique.overall_recommendation == "accept"


def test_no_revision_when_critic_accepts_on_first_pass():
    fake_llm = FakeLLMClient(
        {
            GeneratorOutput: [GEN_OUTPUT],
            CritiqueReport: [CRITIQUE_ACCEPT],
            JudgeOutput: [JUDGE_OUTPUT],
        }
    )
    harness = FakeHarness()

    run_pipeline(build_sample_spec(), fake_llm, harness)

    generator_calls = sum(1 for c in fake_llm.calls if c["output_format"] is GeneratorOutput)
    critic_calls = sum(1 for c in fake_llm.calls if c["output_format"] is CritiqueReport)
    assert generator_calls == 1
    assert critic_calls == 1
