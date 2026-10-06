import pytest
from fastapi.testclient import TestClient

from evals.reference_app.main import create_app


@pytest.fixture
def client():
    """The fixture every generated test file must use for HTTP calls — never
    a hardcoded URL or port. A fresh app/store is built per test function so
    mutant runs can't leak state into each other."""
    return TestClient(create_app())
