import itertools

from evals.reference_app.models import Applicant, Disbursement, LoanApplication


class ReferenceStore:
    """In-memory store. One fresh instance per app — never a module singleton,
    or mutant test runs would leak state into each other (see the harness's
    independence test)."""

    def __init__(self):
        self.applicants: dict[str, Applicant] = {}
        self.loan_applications: dict[str, LoanApplication] = {}
        self.disbursements: dict[str, list[Disbursement]] = {}
        self._counters = {
            "applicant": itertools.count(1),
            "loan": itertools.count(1),
            "disbursement": itertools.count(1),
        }

    def new_id(self, kind: str) -> str:
        return f"{kind}-{next(self._counters[kind])}"


def create_store() -> ReferenceStore:
    return ReferenceStore()
