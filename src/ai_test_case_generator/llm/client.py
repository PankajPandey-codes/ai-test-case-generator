from typing import Protocol, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMClient(Protocol):
    def parse(
        self,
        *,
        system: str,
        messages: list[dict],
        output_format: Type[T],
        effort: str = "high",
    ) -> T: ...


class AnthropicLLMClient:
    """Thin wrapper around anthropic.Anthropic().messages.parse().

    Uses client.messages.parse() with output_format=<PydanticModel>, reading
    response.parsed_output — not output_config.format with manual JSON
    parsing. This is the current SDK's documented path for schema-validated
    responses.

    NOTE: run one manual, real (non-Fake) call locally before relying on
    this in the full pipeline — e.g. AnthropicLLMClient().parse(system=...,
    messages=[...], output_format=SomeModel) — to confirm the installed
    anthropic SDK version's response.parsed_output round-trips as expected,
    and to decide how to handle a response that fails schema validation
    (unhandled here deliberately, since CI never exercises the live API).
    """

    def __init__(self, model: str = "claude-sonnet-5-5", max_tokens: int = 16000):
        import anthropic

        self._client = anthropic.Anthropic()
        self._model = model
        self._max_tokens = max_tokens

    def parse(
        self,
        *,
        system: str,
        messages: list[dict],
        output_format: Type[T],
        effort: str = "high",
    ) -> T:
        response = self._client.messages.parse(
            model=self._model,
            max_tokens=self._max_tokens,
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=messages,
            output_format=output_format,
            output_config={"effort": effort},
        )
        return response.parsed_output
