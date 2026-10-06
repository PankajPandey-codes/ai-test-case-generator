from pathlib import Path

from evals.runner import FIXTURES_DIR
from evals.runner import FileHarness
from ai_test_case_generator.schemas.generator import GeneratorOutput


def test_file_harness_writes_runs_and_cleans_up():
    harness = FileHarness()
    gen_output = GeneratorOutput(
        test_file_code=Path("evals/fixtures/golden_test_suite.py").read_text(),
        test_cases=[],
        assumptions=[],
    )

    before = set(FIXTURES_DIR.glob("_generated_*.py"))
    evidence = harness.evaluate(gen_output)
    after = set(FIXTURES_DIR.glob("_generated_*.py"))

    assert before == after  # temp file cleaned up
    assert evidence.baseline_passed is True
    assert evidence.kill_rate == 5 / 7
