"""Define dynamic fixtures."""
import json

import pytest

from .common import TEST_TOKEN, load_fixture


@pytest.fixture(name="login_response")
def login_response_fixture(token):
    """Define a fixture to return a successful login response."""
    return {"token": token}


@pytest.fixture(name="password_reset_fail_response", scope="session")
def password_reset_fail_response_fixture():
    """Define a fixture to return a failed password reset request response."""
    return json.loads(load_fixture("password_reset_fail_response.json"))


@pytest.fixture(name="token")
def token_fixture():
    """Define a fixture to return a token."""
    return TEST_TOKEN
