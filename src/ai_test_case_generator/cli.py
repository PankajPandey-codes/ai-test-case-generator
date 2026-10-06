import argparse
import datetime
import sys
from pathlib import Path

from ai_test_case_generator.llm.client import AnthropicLLMClient
from ai_test_case_generator.pipeline.orchestrator import run_pipeline
from ai_test_case_generator.specs.mock_banking_api import build_mock_banking_spec
from evals.runner import FileHarness


def generate(output_dir: str | None = None) -> int:
    """Runs the full Generator->Critic->Judge pipeline against the mock
    banking spec using a real Claude API call (requires ANTHROPIC_API_KEY),
    evaluates the generated suite through the mutation-testing harness, and
    writes the generated test file + full report to disk.

    Returns 0 if the gate passed, 1 otherwise — suitable as a process exit
    code for scripting.
    """
    spec = build_mock_banking_spec()
    llm = AnthropicLLMClient()
    harness = FileHarness()

    result = run_pipeline(spec, llm, harness)

    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d-%H%M%S")
    out_dir = Path(output_dir or f"evals/reports/{timestamp}")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "generated_tests.py").write_text(result.generator_output.test_file_code)
    (out_dir / "report.json").write_text(result.model_dump_json(indent=2))

    print(f"Gate: {'PASS' if result.gate.passed else 'FAIL'}")
    print(f"Kill rate: {result.evidence.kill_rate:.2f}  Rubric avg: {result.judge_output.rubric_average:.2f}")
    if result.gate.reasons:
        print("Reasons:", result.gate.reasons)
    print(f"Generated test file: {out_dir / 'generated_tests.py'}")
    print(f"Full report: {out_dir / 'report.json'}")

    return 0 if result.gate.passed else 1


def main() -> None:
    parser = argparse.ArgumentParser(prog="ai-test-case-generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser(
        "generate", help="Run the full pipeline against the mock banking spec"
    )
    generate_parser.add_argument(
        "--output-dir", default=None, help="Where to write generated_tests.py and report.json"
    )

    args = parser.parse_args()

    if args.command == "generate":
        sys.exit(generate(args.output_dir))


if __name__ == "__main__":
    main()
