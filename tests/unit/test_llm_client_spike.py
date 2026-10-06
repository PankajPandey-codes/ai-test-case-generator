from pydantic import BaseModel

from tests.fixtures.fake_llm_client import FakeLLMClient


class EchoSpikeResult(BaseModel):
    essay: str
    word_count: int


def test_fake_llm_client_round_trips_structured_output():
    canned = EchoSpikeResult(essay="word " * 500, word_count=500)
    fake = FakeLLMClient({EchoSpikeResult: [canned]})

    result = fake.parse(
        system="You write long essays.",
        messages=[{"role": "user", "content": "Write a 500-word essay."}],
        output_format=EchoSpikeResult,
    )

    assert result == canned
    assert isinstance(result, EchoSpikeResult)
    assert fake.calls[0]["output_format"] is EchoSpikeResult
