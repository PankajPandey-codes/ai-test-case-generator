# AI Test-Case Generator

A multi-agent pipeline (**Generator → Critic → Judge**) that turns an API spec into a pytest test suite — with a mutation-testing harness that proves the generated tests actually catch real bugs, instead of just looking plausible.

## Why this exists

"An LLM wrote some tests" isn't evidence they're any good. This project's core claim is provable: a reference FastAPI app ships with 7 hand-seeded, named bugs (auth bypass, boundary error, wrong HTTP status, missing validation, a data leak, a bad state transition, an idempotency violation). The generated suite is run against a clean baseline and against each bug individually — whichever bugs make a previously-passing test fail are **killed**. The pipeline only passes its own gate if:

```
baseline passes 100%  AND  kill_rate >= 70%  AND  rubric_average >= 3.5
```

That gate is a plain Python function (`evals/gate.py`) — not an LLM opinion.

## Quickstart

```bash
pip install -e ".[dev]"
export ANTHROPIC_API_KEY=sk-ant-...
ai-test-case-generator generate
```

This runs the full pipeline against the bundled mock banking spec (`LoanApplication`, `Applicant`, `Disbursement` — a generic demo domain, not tied to any real company), and writes:

- `evals/reports/<timestamp>/generated_tests.py` — the actual generated pytest file
- `evals/reports/<timestamp>/report.json` — the full pipeline result: generator output, critique, mutation-testing evidence, judge rubric scores, and the gate verdict

Exit code is `0` if the gate passed, `1` otherwise, so it's scriptable.

## Running the tests

```bash
pytest -v
```

Every test runs against a `FakeLLMClient` test double — no network calls, no API cost, nothing flaky. CI (`.github/workflows/ci.yml`) runs lint + the full suite on every push; it never calls the live Claude API.

## Architecture

```
Generator --(spec)--> pytest file
    |
    v
Critic --(ast.parse syntax check + LLM coverage review)--> accept | revise (capped at one retry)
    |
    v
Harness --(runs suite against 7 seeded-bug mutants, no LLM)--> kill rate
    |
    v
Judge --(rubric score + evidence narrative)--> advisory verdict
    |
    v
Gate --(plain Python)--> pass/fail
```

All three LLM stages use `claude-sonnet-5-5` via `client.messages.parse()` for schema-validated structured output (see `src/ai_test_case_generator/llm/client.py`). No agent framework — the whole orchestration is one ~40-line function (`src/ai_test_case_generator/pipeline/orchestrator.py`), a deliberate choice: the pipeline is a fixed, short DAG with no dynamic routing, so hand-rolled composition with typed contracts at every seam is more legible than a framework would be.

## Cost

A full pipeline run (Generator + Critic + Judge, no revision pass) is roughly 15K input / 8K output tokens across 3 calls on Sonnet 5.5 — about **$0.11/run**. Prompt caching (the spec + system prompt are cached) cuts repeated-run cost further; `response.usage.cache_read_input_tokens` is logged for each stage.

## What's deliberately out of scope (v1)

No generic mutation-testing engine, no multi-spec ingestion, no web UI, no database, no required live-API CI job. See the architecture plan for the full reasoning — this is a few-day portfolio project, not a production platform.

## License

MIT
