from ai_test_case_generator.llm.client import LLMClient
from ai_test_case_generator.schemas.critic import CritiqueReport
from ai_test_case_generator.schemas.evidence import EvidenceReport
from ai_test_case_generator.schemas.generator import GeneratorOutput
from ai_test_case_generator.schemas.judge import RUBRIC_DIMENSIONS, JudgeOutput

JUDGE_SYSTEM_PROMPT = (
    "You are grading a generated pytest test suite on 5 fixed rubric dimensions: "
    "readability, assertion_quality, test_independence, pytest_idioms, and "
    "maintainability. Score each 1-5 with a short justification, and write a "
    "narrative synthesizing the mutation-testing evidence you're given. Your "
    "verdict is advisory only — it does not gate the pipeline."
)


def judge(
    llm: LLMClient,
    gen_output: GeneratorOutput,
    critique: CritiqueReport,
    evidence: EvidenceReport,
) -> JudgeOutput:
    """Judge stage: rubric-scores the suite and narrates the evidence report.

    rubric_average is always computed in code as the mean of the 5 scores —
    never trusted from the LLM's own arithmetic.
    """
    user_content = (
        f"Generated test file:\n{gen_output.test_file_code}\n\n"
        f"Critique report:\n{critique.model_dump_json(indent=2)}\n\n"
        f"Mutation-testing evidence:\n{evidence.model_dump_json(indent=2)}\n\n"
        f"Score exactly these dimensions: {list(RUBRIC_DIMENSIONS)}"
    )

    llm_output = llm.parse(
        system=JUDGE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
        output_format=JudgeOutput,
        effort="medium",
    )

    computed_average = sum(s.score for s in llm_output.rubric_scores) / len(llm_output.rubric_scores)
    return llm_output.model_copy(update={"rubric_average": computed_average})
