import enum

from pydantic import BaseModel


class LoanStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DISBURSED = "disbursed"


class ApplicantCreate(BaseModel):
    name: str
    ssn: str
    annual_income: float


class Applicant(ApplicantCreate):
    id: str


class LoanApplicationCreate(BaseModel):
    applicant_id: str
    amount: float


class LoanApplication(LoanApplicationCreate):
    id: str
    status: LoanStatus


class Disbursement(BaseModel):
    id: str
    loan_application_id: str
    amount: float
    disbursed_at: str
