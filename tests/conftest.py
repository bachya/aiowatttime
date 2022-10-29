"""Define dynamic fixtures."""
from __future__ import annotations

import json
from collections.abc import Generator
from typing import Any, cast

import aiohttp
import pytest
from aresponses import ResponsesMockServer

from .common import load_fixture


@pytest.fixture(name="authenticated_watttime_api_server")
def authenticated_watttime_api_server_fixture(
    login_response: dict[str, Any]
) -> Generator[ResponsesMockServer, None, None]:
    """Return a fixture that mocks an authenticated WattTime API server.

    Args:
        login_response: An API response payload
    """
    server = ResponsesMockServer()
    server.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )
    yield server


@pytest.fixture(name="coordinates_not_found_response", scope="session")
def coordinates_not_found_response_fixture() -> dict[str, Any]:
    """Define a fixture to return a unknown coordinates response.

    Returns:
        An API response payload.
    """
    return cast(
        dict[str, Any], json.loads(load_fixture("coordinates_not_found_response.json"))
    )


@pytest.fixture(name="forbidden_response", scope="session")
def forbidden_response_fixture() -> str:
    """Define a fixture to return an NGINX 403 Forbidden HTML document.

    Returns:
        A parsed NGINX 403 response string.
    """
    return load_fixture("403_forbidden_response.html")


@pytest.fixture(name="forecasted_emissions_response", scope="session")
def forecasted_emissions_response_fixture() -> dict[str, Any]:
    """Define a fixture to return a forecasted emissions response.

    Returns:
        An API response payload.
    """
    return cast(
        dict[str, Any], json.loads(load_fixture("forecasted_emissions_response.json"))
    )


@pytest.fixture(name="grid_region_response", scope="session")
def grid_region_response_fixture() -> dict[str, Any]:
    """Define a fixture to return a grid region response.

    Returns:
        An API response payload.
    """
    return cast(dict[str, Any], json.loads(load_fixture("grid_region_response.json")))


@pytest.fixture(name="historical_emissions_response", scope="session")
def historical_emissions_response_fixture() -> dict[str, Any]:
    """Define a fixture to return a historical emissions response.

    Returns:
        An API response payload.
    """
    return cast(
        dict[str, Any], json.loads(load_fixture("historical_emissions_response.json"))
    )


@pytest.fixture(name="invalid_scope_response", scope="session")
def invalid_scope_response_fixture() -> dict[str, Any]:
    """Define a fixture to return an invalid scope message.

    Returns:
        An API response payload.
    """
    return cast(dict[str, Any], json.loads(load_fixture("invalid_scope_response.json")))


@pytest.fixture(name="login_response")
def login_response_fixture() -> dict[str, Any]:
    """Define a fixture to return a successful login response.

    Returns:
        An API response payload.
    """
    return {"token": "abcd1234"}


@pytest.fixture(name="new_user_success_response")
def new_user_success_response_fixture() -> dict[str, Any]:
    """Define a fixture to return a successful new user registration response.

    Returns:
        An API response payload.
    """
    return {"user": "user", "ok": "User created"}


@pytest.fixture(name="new_user_fail_response", scope="session")
def new_user_fail_response_fixture() -> dict[str, Any]:
    """Define a fixture to return a failed new user registration response.

    Returns:
        An API response payload.
    """
    return cast(dict[str, Any], json.loads(load_fixture("new_user_fail_response.json")))


@pytest.fixture(name="password_reset_fail_response", scope="session")
def password_reset_fail_response_fixture() -> dict[str, Any]:
    """Define a fixture to return a failed password reset request response.

    Returns:
        An API response payload.
    """
    return cast(
        dict[str, Any], json.loads(load_fixture("password_reset_fail_response.json"))
    )


@pytest.fixture(name="realtime_emissions_response", scope="session")
def realtime_emissions_response_fixture() -> dict[str, Any]:
    """Define a fixture to return a realtime emissions response.

    Returns:
        An API response payload.
    """
    return cast(
        dict[str, Any], json.loads(load_fixture("realtime_emissions_response.json"))
    )
