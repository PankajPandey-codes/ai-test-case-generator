from ai_test_case_generator.llm.client import LLMClient
from ai_test_case_generator.schemas.generator import GeneratorInput, GeneratorOutput

GENERATOR_SYSTEM_PROMPT = (
    "You are a senior QA engineer writing pytest test suites against an API spec. "
    "Generate a complete pytest test file covering happy-path, boundary, auth, and "
    "validation cases for every endpoint in the spec. Use the `client` fixture for "
    "all HTTP calls — never hardcode a URL or port."
)


def generate(llm: LLMClient, input: GeneratorInput) -> GeneratorOutput:
    """Generator stage: spec -> candidate pytest file + structured test-case manifest.

    Does not judge or execute its own output — that's Critic's and the eval
    harness's job.
    """
    user_content = (
        f"API spec:\n{input.api_spec.model_dump_json(indent=2)}\n\n"
        f"Style guide:\n{input.style_guide}"
    )
    if input.revision_feedback is not None:
        user_content += f"\n\nRevision feedback from the previous critique:\n{input.revision_feedback}"

    return llm.parse(
        system=GENERATOR_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
        output_format=GeneratorOutput,
        effort="high",
    )
