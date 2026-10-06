import os

SEEDED_BUG_CLASSES = (
    "auth_bypass",
    "wrong_validation_boundary",
    "incorrect_status_code",
    "missing_required_field_check",
    "data_leak_in_response",
    "wrong_status_transition",
    "idempotency_violation",
)


def is_bug_active(bug_name: str) -> bool:
    """Single source of truth for which seeded bug (if any) is active.

    Reads INJECT_BUG fresh on every call (not cached at import time) so a
    test can flip it between a clean run and a buggy run within the same
    process.
    """
    assert bug_name in SEEDED_BUG_CLASSES, f"unknown bug class: {bug_name}"
    return os.environ.get("INJECT_BUG") == bug_name
