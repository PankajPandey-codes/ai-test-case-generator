import pytest
from pydantic import ValidationError

from ai_test_case_generator.schemas.critic import CodeIssue, CoverageGap, CritiqueReport
from ai_test_case_generator.schemas.evidence import EvidenceReport, MutantResult
from ai_test_case_generator.schemas.generator import (
    GeneratedTestCase,
    GeneratorInput,
    GeneratorOutput,
)
from ai_test_case_generator.schemas.judge import JudgeOutput, RubricScore
from ai_test_case_generator.schemas.spec import ApiSpecDoc, EndpointSpec
from tests.fixtures.sample_spec import build_sample_spec


def test_endpoint_spec_and_api_spec_doc_construct():
    endpoint = EndpointSpec(
        path="/applicants", method="POST", description="Create an applicant.", categories=["validation"]
    )
    spec = ApiSpecDoc(title="Mock Banking API", version="0.1.0", endpoints=[endpoint])
    assert spec.endpoints[0].path == "/applicants"


def test_generator_input_and_output_construct():
    spec = build_sample_spec()
    gen_input = GeneratorInput(api_spec=spec, style_guide="Use arrange-act-assert.")
    assert gen_input.revision_feedback is None

    case = GeneratedTestCase(
        id="tc-1",
        name="test_x",
        endpoint="/applicants",
        method="POST",
        category="validation",
        description="Checks validation.",
    )
    output = GeneratorOutput(test_file_code="def test_x():\n    assert True\n", test_cases=[case], assumptions=[])
    assert output.test_cases[0].id == "tc-1"


def test_critique_report_constructs():
    gap = CoverageGap(endpoint="/applicants", category="validation", description="No negative-amount test.")
    issue = CodeIssue(description="Magic number 5000.", severity="low")
    report = CritiqueReport(
        syntax_valid=True, coverage_gaps=[gap], code_issues=[issue], overall_recommendation="accept"
    )
    assert report.overall_recommendation == "accept"


def test_judge_output_constructs():
    scores = [
        RubricScore(dimension=dim, score=4, justification="ok")
        for dim in ("readability", "assertion_quality", "test_independence", "pytest_idioms", "maintainability")
    ]
    output = JudgeOutput(rubric_scores=scores, rubric_average=4.0, narrative="Solid suite.", verdict="pass")
    assert len(output.rubric_scores) == 5


def test_evidence_report_constructs():
    mutant = MutantResult(bug_class="auth_bypass", killed=True, failing_test_ids=["tests.py::test_x"])
    report = EvidenceReport(baseline_passed=True, mutant_results=[mutant], kill_rate=1 / 7)
    assert report.mutant_results[0].killed is True


def test_generator_input_missing_style_guide_raises():
    spec = build_sample_spec()
    with pytest.raises(ValidationError):
        GeneratorInput(api_spec=spec)


def test_judge_output_missing_narrative_raises():
    scores = [RubricScore(dimension="readability", score=4, justification="ok")]
    with pytest.raises(ValidationError):
        JudgeOutput(rubric_scores=scores, rubric_average=4.0, verdict="pass")
