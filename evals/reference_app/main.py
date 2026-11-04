import datetime

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

from evals.reference_app.bugs import is_bug_active
from evals.reference_app.models import (
    Applicant,
    ApplicantCreate,
    Disbursement,
    LoanApplication,
    LoanApplicationCreate,
    LoanStatus,
)
from evals.reference_app.store import create_store

ADMIN_TOKEN = "secret-admin-token"
MIN_LOAN_AMOUNT = 1000
MAX_LOAN_AMOUNT = 100000


def create_app() -> FastAPI:
    """Factory: builds a brand-new app with a brand-new store on every call.
    Never promote this to a module-level singleton — mutant runs depend on
    fresh, unshared state."""
    app = FastAPI(title="Mock Banking API")
    store = create_store()

    @app.post("/applicants", status_code=201)
    def create_applicant(payload: ApplicantCreate):
        if not is_bug_active("missing_required_field_check") and payload.annual_income <= 0:
            raise HTTPException(status_code=422, detail="annual_income must be positive")
        applicant_id = store.new_id("applicant")
        applicant = Applicant(id=applicant_id, **payload.model_dump())
        store.applicants[applicant_id] = applicant
        return applicant.model_dump()

    @app.get("/applicants/{applicant_id}")
    def get_applicant(applicant_id: str):
        applicant = store.applicants.get(applicant_id)
        if applicant is None:
            raise HTTPException(status_code=404, detail="applicant not found")
        data = applicant.model_dump()
        if not is_bug_active("data_leak_in_response"):
            data.pop("ssn", None)
        return data

    @app.post("/loan-applications", status_code=201)
    def create_loan_application(payload: LoanApplicationCreate):
        if payload.applicant_id not in store.applicants:
            raise HTTPException(status_code=404, detail="applicant not found")
        max_amount = MAX_LOAN_AMOUNT
        if is_bug_active("wrong_validation_boundary"):
            max_amount = 10_000_000
        if not (MIN_LOAN_AMOUNT <= payload.amount <= max_amount):
            raise HTTPException(status_code=422, detail="amount out of bounds")
        loan_id = store.new_id("loan")
        loan = LoanApplication(id=loan_id, status=LoanStatus.PENDING, **payload.model_dump())
        store.loan_applications[loan_id] = loan
        return loan.model_dump()

    @app.get("/loan-applications/{loan_id}")
    def get_loan_application(loan_id: str):
        loan = store.loan_applications.get(loan_id)
        if loan is None:
            if is_bug_active("incorrect_status_code"):
                return JSONResponse(status_code=200, content=None)
            raise HTTPException(status_code=404, detail="loan application not found")
        return loan.model_dump()

    @app.post("/loan-applications/{loan_id}/approve")
    def approve_loan_application(loan_id: str, x_admin_token: str | None = Header(default=None)):
        loan = store.loan_applications.get(loan_id)
        if loan is None:
            raise HTTPException(status_code=404, detail="loan application not found")
        if not is_bug_active("auth_bypass") and x_admin_token != ADMIN_TOKEN:
            raise HTTPException(status_code=403, detail="admin token required")
        if not is_bug_active("wrong_status_transition") and loan.status != LoanStatus.PENDING:
            raise HTTPException(status_code=409, detail="loan is not pending")
        loan.status = LoanStatus.APPROVED
        return loan.model_dump()

    @app.post("/loan-applications/{loan_id}/disburse", status_code=201)
    def disburse_loan_application(loan_id: str):
        loan = store.loan_applications.get(loan_id)
        if loan is None:
            raise HTTPException(status_code=404, detail="loan application not found")
        existing = store.disbursements.get(loan_id, [])
        if existing:
            if is_bug_active("idempotency_violation"):
                disbursement = Disbursement(
                    id=store.new_id("disbursement"),
                    loan_application_id=loan_id,
                    amount=loan.amount,
                    disbursed_at=datetime.datetime.now(datetime.UTC).isoformat(),
                )
                store.disbursements[loan_id].append(disbursement)
                return disbursement.model_dump()
            return JSONResponse(status_code=200, content=existing[0].model_dump())
        if loan.status != LoanStatus.APPROVED:
            raise HTTPException(status_code=409, detail="loan is not approved")
        disbursement = Disbursement(
            id=store.new_id("disbursement"),
            loan_application_id=loan_id,
            amount=loan.amount,
            disbursed_at=datetime.datetime.now(datetime.UTC).isoformat(),
        )
        store.disbursements.setdefault(loan_id, []).append(disbursement)
        loan.status = LoanStatus.DISBURSED
        return disbursement.model_dump()

    return app
