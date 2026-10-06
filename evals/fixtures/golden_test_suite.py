"""Hand-written reference suite used by the harness's own tests and by CI
Job 2 (`--mode recorded`). Deliberately kills 5 of the 7 seeded mutants
(kill_rate ~0.714, clears the 0.70 gate) and deliberately leaves
wrong_status_transition and idempotency_violation unkilled, so the harness's
kill-rate arithmetic is provably exercised rather than trivially 100% or 0%.
"""


def test_create_applicant_requires_positive_income(client):
    resp = client.post("/applicants", json={"name": "A", "ssn": "1", "annual_income": 0})
    assert resp.status_code == 422


def test_loan_amount_rejected_above_max(client):
    applicant = client.post(
        "/applicants", json={"name": "A", "ssn": "1", "annual_income": 50000}
    ).json()
    resp = client.post(
        "/loan-applications", json={"applicant_id": applicant["id"], "amount": 500000}
    )
    assert resp.status_code == 422


def test_get_missing_loan_application_returns_404(client):
    resp = client.get("/loan-applications/does-not-exist")
    assert resp.status_code == 404


def test_get_applicant_does_not_leak_ssn(client):
    applicant = client.post(
        "/applicants", json={"name": "A", "ssn": "1", "annual_income": 50000}
    ).json()
    resp = client.get(f"/applicants/{applicant['id']}")
    assert "ssn" not in resp.json()


def test_approve_requires_admin_token(client):
    applicant = client.post(
        "/applicants", json={"name": "A", "ssn": "1", "annual_income": 50000}
    ).json()
    loan = client.post(
        "/loan-applications", json={"applicant_id": applicant["id"], "amount": 5000}
    ).json()
    resp = client.post(f"/loan-applications/{loan['id']}/approve")
    assert resp.status_code == 403
