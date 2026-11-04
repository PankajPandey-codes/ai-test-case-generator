from fastapi.testclient import TestClient

from evals.reference_app.main import create_app


def test_create_app_returns_independent_state_across_calls():
    """A mutant run must never see state created by a previous run's app
    instance — create_app() must build a fresh store every time, not reuse
    a module-level singleton."""
    first_client = TestClient(create_app())
    resp = first_client.post(
        "/applicants", json={"name": "Jane Doe", "ssn": "123-45-6789", "annual_income": 50000}
    )
    applicant_id = resp.json()["id"]

    second_client = TestClient(create_app())
    not_found = second_client.get(f"/applicants/{applicant_id}")

    assert not_found.status_code == 404
