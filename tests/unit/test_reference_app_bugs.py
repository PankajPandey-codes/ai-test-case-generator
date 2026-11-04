import os

import pytest
from fastapi.testclient import TestClient

from evals.reference_app.main import create_app


@pytest.fixture
def client_factory():
    def _make(bug: str | None):
        if bug is None:
            os.environ.pop("INJECT_BUG", None)
        else:
            os.environ["INJECT_BUG"] = bug
        app = create_app()
        return TestClient(app)

    yield _make
    os.environ.pop("INJECT_BUG", None)


def _create_applicant(client, annual_income=50000):
    resp = client.post(
        "/applicants",
        json={"name": "Jane Doe", "ssn": "123-45-6789", "annual_income": annual_income},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _create_loan(client, applicant_id, amount=5000):
    resp = client.post(
        "/loan-applications",
        json={"applicant_id": applicant_id, "amount": amount},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_auth_bypass_is_observable(client_factory):
    clean = client_factory(None)
    applicant_id = _create_applicant(clean)
    loan_id = _create_loan(clean, applicant_id)
    denied = clean.post(f"/loan-applications/{loan_id}/approve")
    assert denied.status_code == 403

    buggy = client_factory("auth_bypass")
    applicant_id = _create_applicant(buggy)
    loan_id = _create_loan(buggy, applicant_id)
    bypassed = buggy.post(f"/loan-applications/{loan_id}/approve")
    assert bypassed.status_code == 200


def test_wrong_validation_boundary_is_observable(client_factory):
    clean = client_factory(None)
    applicant_id = _create_applicant(clean)
    rejected = clean.post(
        "/loan-applications", json={"applicant_id": applicant_id, "amount": 500_000}
    )
    assert rejected.status_code == 422

    buggy = client_factory("wrong_validation_boundary")
    applicant_id = _create_applicant(buggy)
    accepted = buggy.post(
        "/loan-applications", json={"applicant_id": applicant_id, "amount": 500_000}
    )
    assert accepted.status_code == 201


def test_incorrect_status_code_is_observable(client_factory):
    clean = client_factory(None)
    not_found = clean.get("/loan-applications/does-not-exist")
    assert not_found.status_code == 404

    buggy = client_factory("incorrect_status_code")
    wrong_code = buggy.get("/loan-applications/does-not-exist")
    assert wrong_code.status_code == 200


def test_missing_required_field_check_is_observable(client_factory):
    clean = client_factory(None)
    rejected = clean.post(
        "/applicants", json={"name": "Jane Doe", "ssn": "123-45-6789", "annual_income": 0}
    )
    assert rejected.status_code == 422

    buggy = client_factory("missing_required_field_check")
    accepted = buggy.post(
        "/applicants", json={"name": "Jane Doe", "ssn": "123-45-6789", "annual_income": 0}
    )
    assert accepted.status_code == 201


def test_data_leak_in_response_is_observable(client_factory):
    clean = client_factory(None)
    applicant_id = _create_applicant(clean)
    safe = clean.get(f"/applicants/{applicant_id}")
    assert "ssn" not in safe.json()

    buggy = client_factory("data_leak_in_response")
    applicant_id = _create_applicant(buggy)
    leaked = buggy.get(f"/applicants/{applicant_id}")
    assert "ssn" in leaked.json()


def test_wrong_status_transition_is_observable(client_factory):
    clean = client_factory(None)
    applicant_id = _create_applicant(clean)
    loan_id = _create_loan(clean, applicant_id)
    clean.post(f"/loan-applications/{loan_id}/approve", headers={"x-admin-token": "secret-admin-token"})
    rejected = clean.post(
        f"/loan-applications/{loan_id}/approve", headers={"x-admin-token": "secret-admin-token"}
    )
    assert rejected.status_code == 409

    buggy = client_factory("wrong_status_transition")
    applicant_id = _create_applicant(buggy)
    loan_id = _create_loan(buggy, applicant_id)
    buggy.post(f"/loan-applications/{loan_id}/approve", headers={"x-admin-token": "secret-admin-token"})
    double_approved = buggy.post(
        f"/loan-applications/{loan_id}/approve", headers={"x-admin-token": "secret-admin-token"}
    )
    assert double_approved.status_code == 200


def test_idempotency_violation_is_observable(client_factory):
    clean = client_factory(None)
    applicant_id = _create_applicant(clean)
    loan_id = _create_loan(clean, applicant_id)
    clean.post(f"/loan-applications/{loan_id}/approve", headers={"x-admin-token": "secret-admin-token"})
    first = clean.post(f"/loan-applications/{loan_id}/disburse")
    second = clean.post(f"/loan-applications/{loan_id}/disburse")
    assert first.json()["id"] == second.json()["id"]

    buggy = client_factory("idempotency_violation")
    applicant_id = _create_applicant(buggy)
    loan_id = _create_loan(buggy, applicant_id)
    buggy.post(f"/loan-applications/{loan_id}/approve", headers={"x-admin-token": "secret-admin-token"})
    first = buggy.post(f"/loan-applications/{loan_id}/disburse")
    second = buggy.post(f"/loan-applications/{loan_id}/disburse")
    assert first.json()["id"] != second.json()["id"]
