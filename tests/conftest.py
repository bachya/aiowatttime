"""Define dynamic fixtures."""
import pytest

from .common import TEST_TOKEN


@pytest.fixture(name="login_response")
def login_response_fixture(token):
    """Define a fixture to return a successful login response."""
    return {"token": token}


@pytest.fixture(name="token")
def token_fixture():
    """Define a fixture to return a token."""
    return TEST_TOKEN
