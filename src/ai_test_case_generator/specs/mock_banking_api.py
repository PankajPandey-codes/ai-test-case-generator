from ai_test_case_generator.schemas.spec import ApiSpecDoc, EndpointSpec


def build_mock_banking_spec() -> ApiSpecDoc:
    """The one demo spec this project generates tests against — a generic
    mock banking API, deliberately not tied to any real employer's domain."""
    return ApiSpecDoc(
        title="Mock Banking API",
        version="0.1.0",
        endpoints=[
            EndpointSpec(
                path="/applicants",
                method="POST",
                description="Create an applicant.",
                categories=["validation", "required_fields"],
            ),
            EndpointSpec(
                path="/applicants/{applicant_id}",
                method="GET",
                description="Fetch an applicant by id.",
                categories=["privacy"],
            ),
            EndpointSpec(
                path="/loan-applications",
                method="POST",
                description="Create a loan application.",
                categories=["validation"],
            ),
            EndpointSpec(
                path="/loan-applications/{loan_id}/approve",
                method="POST",
                description="Approve a pending loan application.",
                categories=["auth", "state_machine"],
            ),
            EndpointSpec(
                path="/loan-applications/{loan_id}/disburse",
                method="POST",
                description="Disburse an approved loan application.",
                categories=["idempotency", "state_machine"],
            ),
        ],
    )
