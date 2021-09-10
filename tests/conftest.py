"""Define dynamic fixtures."""
import json

import pytest

from .common import load_fixture


@pytest.fixture(name="login_response")
def login_response_fixture(token):
    """Define a fixture to return a successful login response."""
    return {"token": token}


@pytest.fixture(name="new_user_success_response")
def new_user_success_response_fixture(username):
    """Define a fixture to return a successful login response."""
    return {"user": username, "ok": "User created"}


@pytest.fixture(name="new_user_fail_response", scope="session")
def new_user_fail_response_fixture():
    """Define a fixture to return a failed password reset request response."""
    return json.loads(load_fixture("new_user_fail_response.json"))


@pytest.fixture(name="password_reset_fail_response", scope="session")
def password_reset_fail_response_fixture():
    """Define a fixture to return a failed password reset request response."""
    return json.loads(load_fixture("password_reset_fail_response.json"))


@pytest.fixture(name="token")
def token_fixture():
    """Define a fixture to return a token."""
    return "abcd1234"


@pytest.fixture(name="username")
def username_fixture():
    """Define a fixture to return a username."""
    return "user"
