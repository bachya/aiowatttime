"""Define tests for the client."""
# pylint: disable=protected-access
import json

import aiohttp
import pytest

from aiowatttime import Client
from aiowatttime.errors import InvalidCredentialsError, RequestError, UsernameTakenError


@pytest.mark.asyncio
async def test_expired_token(
    aresponses, forbidden_response, realtime_emissions_response, login_response
):
    """Test that an expired token is handled correctly."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        aresponses.Response(
            text=json.dumps(login_response),
            status=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
        ),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/index",
        "get",
        aresponses.Response(
            text=json.dumps(realtime_emissions_response),
            status=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
        ),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/index",
        "get",
        aresponses.Response(
            text=forbidden_response, status=403, headers={"Content-Type": "text/html"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = await Client.async_login("user", "password", session=session)

        # Simulate request #1 having a working token:
        await client.emissions.async_get_realtime_emissions("40.6971494", "-74.2598655")

        # Simulate request #2 having an expired token:
        with pytest.raises(InvalidCredentialsError):
            await client.emissions.async_get_realtime_emissions(
                "40.6971494", "-74.2598655"
            )


@pytest.mark.asyncio
async def test_get_client(aresponses, login_response):
    """Test getting an authenticated client."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        aresponses.Response(
            text=json.dumps(login_response),
            status=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = await Client.async_login("user", "password", session=session)
        assert client._token == "abcd1234"


@pytest.mark.asyncio
async def test_get_client_new_session(aresponses, login_response):
    """Test getting an authenticated client without an explicit aiohttp ClientSession."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        aresponses.Response(
            text=json.dumps(login_response),
            status=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
        ),
    )

    client = await Client.async_login("user", "password")
    assert client._token == "abcd1234"


@pytest.mark.asyncio
async def test_get_new_token(aresponses, login_response):
    """Test getting a new token with an authenticated client."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        aresponses.Response(
            text=json.dumps(login_response),
            status=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
        ),
    )

    login_response = {"token": "efgh5678"}

    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        aresponses.Response(
            text=json.dumps(login_response),
            status=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = await Client.async_login("user", "password", session=session)
        assert client._token == "abcd1234"
        await client.async_authenticate()
        assert client._token == "efgh5678"


@pytest.mark.asyncio
async def test_register_new_username_fail(aresponses, new_user_fail_response):
    """Test that a failed new user registration is handled correctly."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/register",
        "post",
        aresponses.Response(
            text=json.dumps(new_user_fail_response),
            status=400,
            headers={"Content-Type": "application/json; charset=utf-8"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        with pytest.raises(UsernameTakenError) as err:
            await Client.async_register_new_username(
                "user",
                "password",
                "email@email.com",
                "My Organization",
                session=session,
            )
        assert "That username is taken. Please choose another." in str(err)


@pytest.mark.asyncio
async def test_register_new_username_success(aresponses, new_user_success_response):
    """Test a successful new user registration."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/register",
        "post",
        aresponses.Response(
            text=json.dumps(new_user_success_response),
            status=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        resp = await Client.async_register_new_username(
            "user", "password", "email@email.com", "My Organization", session=session
        )
        assert resp == {"user": "user", "ok": "User created"}


@pytest.mark.asyncio
async def test_request_password_reset_fail(
    aresponses, login_response, password_reset_fail_response
):
    """Test that a failed password reset request is handled correctly."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        aresponses.Response(
            text=json.dumps(login_response),
            status=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
        ),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/password",
        "get",
        aresponses.Response(
            text=json.dumps(password_reset_fail_response),
            status=400,
            headers={"Content-Type": "application/json; charset=utf-8"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = await Client.async_login("user", "password", session=session)
        with pytest.raises(RequestError) as err:
            await client.async_request_password_reset()
        assert "A problem occurred, your request could not be processed" in str(err)
