from typing import Protocol

from ai_test_case_generator.llm.client import LLMClient
from ai_test_case_generator.pipeline.critic import critique_tests
from ai_test_case_generator.pipeline.generator import generate
from ai_test_case_generator.pipeline.judge import judge
from ai_test_case_generator.schemas.evidence import EvidenceReport
from ai_test_case_generator.schemas.generator import GeneratorInput, GeneratorOutput
from ai_test_case_generator.schemas.pipeline import PipelineResult
from ai_test_case_generator.schemas.spec import ApiSpecDoc
from evals.gate import compute_gate

STYLE_GUIDE = "Use the `client` fixture for all HTTP calls. Follow arrange-act-assert. One assertion focus per test."


class Harness(Protocol):
    def evaluate(self, gen_output: GeneratorOutput) -> EvidenceReport: ...


def run_pipeline(spec: ApiSpecDoc, llm: LLMClient, harness: Harness) -> PipelineResult:
    """Generator -> Critic -> (exactly one revision pass if Critic says
    "revise", never more) -> harness.evaluate (no LLM call) -> Judge ->
    compute_gate. A fixed, short DAG — no dynamic routing, no open-ended
    iteration.
    """
    gen_output = generate(llm, GeneratorInput(api_spec=spec, style_guide=STYLE_GUIDE))
    critique = critique_tests(llm, gen_output, spec)

    if critique.overall_recommendation == "revise":
        gen_output = generate(
            llm,
            GeneratorInput(
                api_spec=spec, style_guide=STYLE_GUIDE, revision_feedback=critique.model_dump_json()
            ),
        )
        critique = critique_tests(llm, gen_output, spec)

    evidence = harness.evaluate(gen_output)
    judge_output = judge(llm, gen_output, critique, evidence)
    gate = compute_gate(evidence, judge_output)

    return PipelineResult(
        generator_output=gen_output,
        critique=critique,
        evidence=evidence,
        judge_output=judge_output,
        gate=gate,
    )
