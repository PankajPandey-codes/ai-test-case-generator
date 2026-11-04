from evals.runner import run_suite

GOLDEN_SUITE_PATH = "evals/fixtures/golden_test_suite.py"


def test_run_suite_against_golden_suite_matches_expected_kill_rate():
    """The golden suite is hand-built to kill exactly 5 of the 7 seeded bugs
    (auth_bypass, wrong_validation_boundary, incorrect_status_code,
    missing_required_field_check, data_leak_in_response) and leave
    wrong_status_transition and idempotency_violation unkilled."""
    evidence = run_suite(GOLDEN_SUITE_PATH)

    assert evidence.baseline_passed is True
    assert evidence.kill_rate == 5 / 7

    killed = {m.bug_class for m in evidence.mutant_results if m.killed}
    assert killed == {
        "auth_bypass",
        "wrong_validation_boundary",
        "incorrect_status_code",
        "missing_required_field_check",
        "data_leak_in_response",
    }
