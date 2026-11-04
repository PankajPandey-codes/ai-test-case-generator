from ai_test_case_generator.pipeline.generator import generate
from ai_test_case_generator.schemas.generator import (
    GeneratedTestCase,
    GeneratorInput,
    GeneratorOutput,
)
from tests.fixtures.fake_llm_client import FakeLLMClient
from tests.fixtures.sample_spec import build_sample_spec

CANNED_OUTPUT = GeneratorOutput(
    test_file_code="def test_x():\n    assert True\n",
    test_cases=[
        GeneratedTestCase(
            id="tc-1", name="test_x", endpoint="/applicants", method="POST",
            category="validation", description="Checks validation.",
        )
    ],
    assumptions=["auth header is X-Admin-Token"],
)


def test_generate_returns_canned_output_and_sends_spec_and_style_guide():
    fake = FakeLLMClient({GeneratorOutput: [CANNED_OUTPUT]})
    spec = build_sample_spec()
    result = generate(fake, GeneratorInput(api_spec=spec, style_guide="Use arrange-act-assert."))

    assert result == CANNED_OUTPUT
    sent_content = fake.calls[0]["messages"][0]["content"]
    assert "Mock Banking API" in sent_content
    assert "arrange-act-assert" in sent_content
    assert "Revision feedback" not in sent_content


def test_generate_includes_revision_feedback_only_when_provided():
    fake = FakeLLMClient({GeneratorOutput: [CANNED_OUTPUT]})
    spec = build_sample_spec()
    generate(
        fake,
        GeneratorInput(
            api_spec=spec,
            style_guide="Use arrange-act-assert.",
            revision_feedback="Add a boundary test for min loan amount.",
        ),
    )

    sent_content = fake.calls[0]["messages"][0]["content"]
    assert "Revision feedback" in sent_content
    assert "min loan amount" in sent_content
