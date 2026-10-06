import ast

from ai_test_case_generator.llm.client import LLMClient
from ai_test_case_generator.schemas.critic import CritiqueReport
from ai_test_case_generator.schemas.generator import GeneratorOutput
from ai_test_case_generator.schemas.spec import ApiSpecDoc

CRITIC_SYSTEM_PROMPT = (
    "You are a meticulous code reviewer. Given an API spec and a generated pytest "
    "file, identify coverage gaps against the spec's endpoints/categories and code "
    "quality issues. Recommend 'accept' only if coverage is adequate and there are "
    "no high-severity issues; otherwise recommend 'revise'."
)


def _is_syntax_valid(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def critique_tests(llm: LLMClient, gen_output: GeneratorOutput, spec: ApiSpecDoc) -> CritiqueReport:
    """Critic stage: deterministic syntax check (never trusted to the LLM) plus
    an LLM pass for spec-coverage gaps and code smells.
    """
    syntax_valid = _is_syntax_valid(gen_output.test_file_code)

    user_content = (
        f"API spec:\n{spec.model_dump_json(indent=2)}\n\n"
        f"Generated test file:\n{gen_output.test_file_code}\n\n"
        f"Test case manifest:\n{[tc.model_dump() for tc in gen_output.test_cases]}"
    )

    llm_report = llm.parse(
        system=CRITIC_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
        output_format=CritiqueReport,
        effort="medium",
    )

    # syntax_valid is always the deterministic ast.parse result — never the
    # LLM's opinion, and an invalid-syntax file forces a revise.
    overall_recommendation = llm_report.overall_recommendation
    if not syntax_valid:
        overall_recommendation = "revise"

    return llm_report.model_copy(update={"syntax_valid": syntax_valid, "overall_recommendation": overall_recommendation})
