from ai_test_case_generator.pipeline.critic import critique_tests
from ai_test_case_generator.schemas.critic import CritiqueReport
from ai_test_case_generator.schemas.generator import GeneratedTestCase, GeneratorOutput
from tests.fixtures.fake_llm_client import FakeLLMClient
from tests.fixtures.sample_spec import build_sample_spec

CASE = GeneratedTestCase(
    id="tc-1", name="test_x", endpoint="/applicants", method="POST",
    category="validation", description="Checks validation.",
)

LLM_SAYS_ACCEPT = CritiqueReport(
    syntax_valid=True,  # ignored by critique_tests — always recomputed deterministically
    coverage_gaps=[],
    code_issues=[],
    overall_recommendation="accept",
)


def test_valid_code_keeps_llm_recommendation():
    fake = FakeLLMClient({CritiqueReport: [LLM_SAYS_ACCEPT]})
    gen_output = GeneratorOutput(
        test_file_code="def test_x():\n    assert True\n", test_cases=[CASE], assumptions=[]
    )
    report = critique_tests(fake, gen_output, build_sample_spec())

    assert report.syntax_valid is True
    assert report.overall_recommendation == "accept"


def test_invalid_syntax_is_caught_deterministically_and_forces_revise():
    fake = FakeLLMClient({CritiqueReport: [LLM_SAYS_ACCEPT]})
    gen_output = GeneratorOutput(
        test_file_code="def test_x(:\n    assert True\n",  # syntax error: stray colon
        test_cases=[CASE],
        assumptions=[],
    )
    report = critique_tests(fake, gen_output, build_sample_spec())

    assert report.syntax_valid is False
    assert report.overall_recommendation == "revise"
