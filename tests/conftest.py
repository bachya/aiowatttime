"""Define dynamic fixtures."""
import json

import pytest

from .common import load_fixture


@pytest.fixture(name="coordinates_not_found_response", scope="session")
def coordinates_not_found_response_fixture():
    """Define a fixture to return a unknown coordinates response."""
    return json.loads(load_fixture("coordinates_not_found_response.json"))


@pytest.fixture(name="forbidden_response", scope="session")
def forbidden_response_fixture():
    """Define a fixture to return an NGINX 403 Forbidden HTML document."""
    return load_fixture("403_forbidden_response.html")


@pytest.fixture(name="forecasted_emissions_response", scope="session")
def forecasted_emissions_response_fixture():
    """Define a fixture to return a forecasted emissions response."""
    return json.loads(load_fixture("forecasted_emissions_response.json"))


@pytest.fixture(name="grid_region_response", scope="session")
def grid_region_response_fixture():
    """Define a fixture to return a grid region response."""
    return json.loads(load_fixture("grid_region_response.json"))


@pytest.fixture(name="historical_emissions_response", scope="session")
def historical_emissions_response_fixture():
    """Define a fixture to return a historical emissions response."""
    return json.loads(load_fixture("historical_emissions_response.json"))


@pytest.fixture(name="invalid_scope_response", scope="session")
def invalid_scope_response_fixture():
    """Define a fixture to return an invalid scope message."""
    return json.loads(load_fixture("invalid_scope_response.json"))


@pytest.fixture(name="login_response")
def login_response_fixture():
    """Define a fixture to return a successful login response."""
    return {"token": "abcd1234"}


@pytest.fixture(name="new_user_success_response")
def new_user_success_response_fixture():
    """Define a fixture to return a successful new user registration response."""
    return {"user": "user", "ok": "User created"}


@pytest.fixture(name="new_user_fail_response", scope="session")
def new_user_fail_response_fixture():
    """Define a fixture to return a failed new user registration response."""
    return json.loads(load_fixture("new_user_fail_response.json"))


@pytest.fixture(name="password_reset_fail_response", scope="session")
def password_reset_fail_response_fixture():
    """Define a fixture to return a failed password reset request response."""
    return json.loads(load_fixture("password_reset_fail_response.json"))


@pytest.fixture(name="realtime_emissions_response", scope="session")
def realtime_emissions_response_fixture():
    """Define a fixture to return a realtime emissions response."""
    return json.loads(load_fixture("realtime_emissions_response.json"))
