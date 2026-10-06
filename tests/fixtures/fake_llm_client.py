from typing import Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class FakeLLMClient:
    """Test double for ai_test_case_generator.llm.client.LLMClient.

    Returns pre-built Pydantic responses from an in-memory queue, keyed by
    output_format type, so tests never make a network call. Each call is
    recorded in self.calls for assertions on prompt content and call counts.
    """

    def __init__(self, responses: dict[type, list[BaseModel]]):
        self._responses = {output_type: list(items) for output_type, items in responses.items()}
        self.calls: list[dict] = []

    def parse(
        self,
        *,
        system: str,
        messages: list[dict],
        output_format: Type[T],
        effort: str = "high",
    ) -> T:
        self.calls.append(
            {"system": system, "messages": messages, "output_format": output_format, "effort": effort}
        )
        queue = self._responses.get(output_format)
        if not queue:
            raise AssertionError(f"FakeLLMClient has no canned response left for {output_format}")
        return queue.pop(0)
