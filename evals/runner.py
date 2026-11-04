import os
import subprocess
import sys
import uuid
from pathlib import Path

from ai_test_case_generator.schemas.evidence import EvidenceReport, MutantResult
from ai_test_case_generator.schemas.generator import GeneratorOutput
from evals.reference_app.bugs import SEEDED_BUG_CLASSES

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _run_pytest(test_file_path: str, bug: str | None) -> set[str]:
    """Runs pytest against test_file_path in a fresh subprocess (so the
    client fixture builds a fresh app/store with no leakage between runs)
    and returns the set of failing test node ids."""
    env = os.environ.copy()
    if bug is None:
        env.pop("INJECT_BUG", None)
    else:
        env["INJECT_BUG"] = bug

    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file_path, "-q", "--tb=no", "--no-header"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    failing = set()
    for line in result.stdout.splitlines():
        if line.startswith("FAILED "):
            failing.add(line.split(" ")[1])
    return failing


def run_suite(test_file_path: str) -> EvidenceReport:
    """Runs the baseline (no injected bug) and all 7 seeded mutants against
    the given generated test file. A test file must use the `client` fixture
    from evals/fixtures/conftest.py — place generated suites under
    evals/fixtures/ (or anywhere that conftest is discoverable) so pytest
    picks it up.

    kill_rate = (mutants whose failing-test set gained a NEW failure vs.
    baseline) / 7. A mutant that breaks an unrelated test still counts as
    killed — a documented, acceptable simplification (slight
    over-crediting, never under-crediting).
    """
    baseline_failures = _run_pytest(test_file_path, None)
    baseline_passed = len(baseline_failures) == 0

    mutant_results = []
    killed_count = 0
    for bug in SEEDED_BUG_CLASSES:
        mutant_failures = _run_pytest(test_file_path, bug)
        new_failures = mutant_failures - baseline_failures
        killed = len(new_failures) > 0
        if killed:
            killed_count += 1
        mutant_results.append(
            MutantResult(bug_class=bug, killed=killed, failing_test_ids=sorted(new_failures))
        )

    kill_rate = killed_count / len(SEEDED_BUG_CLASSES)
    return EvidenceReport(
        baseline_passed=baseline_passed, mutant_results=mutant_results, kill_rate=kill_rate
    )


class FileHarness:
    """Adapts run_suite() to the orchestrator's Harness protocol
    (evaluate(gen_output) -> EvidenceReport). Writes the generated code to a
    throwaway file under evals/fixtures/ (so conftest.py's `client` fixture
    is discoverable), runs the harness, then deletes the file."""

    def evaluate(self, gen_output: GeneratorOutput) -> EvidenceReport:
        temp_path = FIXTURES_DIR / f"_generated_{uuid.uuid4().hex}.py"
        temp_path.write_text(gen_output.test_file_code)
        try:
            return run_suite(str(temp_path))
        finally:
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("suite", help="Path to a generated pytest test file")
    args = parser.parse_args()
    evidence = run_suite(args.suite)
    print(evidence.model_dump_json(indent=2))
