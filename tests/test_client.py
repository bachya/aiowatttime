"""Define tests for the client."""
# pylint: disable=protected-access
import logging

import aiohttp
import pytest

from aiowatttime import Client
from aiowatttime.errors import InvalidCredentialsError, RequestError, UsernameTakenError


@pytest.mark.asyncio
async def test_custom_logger(aresponses, caplog, login_response):
    """Test that a custom logger is used when provided to the client."""
    caplog.set_level(logging.DEBUG)
    custom_logger = logging.getLogger("custom")

    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )

    async with aiohttp.ClientSession() as session:
        await Client.async_login(
            "user", "password", session=session, logger=custom_logger,
        )
        assert any(
            record.name == "custom" and "Received data" in record.message
            for record in caplog.records
        )

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_expired_token(
    aresponses, forbidden_response, realtime_emissions_response, login_response
):
    """Test a scenario where multiple token refreshes don't work."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/index",
        "get",
        response=aiohttp.web_response.json_response(
            realtime_emissions_response, status=200
        ),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/index",
        "get",
        response=aresponses.Response(
            text=forbidden_response, status=403, headers={"Content-Type": "text/html"},
        ),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/index",
        "get",
        response=aresponses.Response(
            text=forbidden_response, status=403, headers={"Content-Type": "text/html"},
        ),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/index",
        "get",
        response=aresponses.Response(
            text=forbidden_response, status=403, headers={"Content-Type": "text/html"},
        ),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )

    async with aiohttp.ClientSession() as session:
        client = await Client.async_login(
            "user",
            "password",
            session=session,
            # We set a 0 delay so that this test is unnecessarily slowed down:
            request_retry_delay=0,
        )

        # Simulate request #1 having a working token:
        await client.emissions.async_get_realtime_emissions("40.6971494", "-74.2598655")

        # Simulate request #2 having an expired token:
        with pytest.raises(InvalidCredentialsError):
            await client.emissions.async_get_realtime_emissions(
                "40.6971494", "-74.2598655"
            )

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_get_client(aresponses, login_response):
    """Test getting an authenticated client."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )

    async with aiohttp.ClientSession() as session:
        client = await Client.async_login("user", "password", session=session)
        assert client._token == "abcd1234"

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_get_client_new_session(aresponses, login_response):
    """Test getting an authenticated client without an explicit aiohttp ClientSession."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )

    client = await Client.async_login("user", "password")
    assert client._token == "abcd1234"
    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_get_new_token(aresponses, login_response):
    """Test getting a new token with an authenticated client."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )

    login_response = {"token": "efgh5678"}

    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )

    async with aiohttp.ClientSession() as session:
        client = await Client.async_login("user", "password", session=session)
        assert client._token == "abcd1234"
        await client.async_authenticate()
        assert client._token == "efgh5678"

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_invalid_credentials(aresponses, forbidden_response):
    """Test that invalid credentials on login are dealt with immediately (no retry)."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aresponses.Response(
            text=forbidden_response, status=403, headers={"Content-Type": "text/html"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        with pytest.raises(InvalidCredentialsError):
            await Client.async_login("user", "password", session=session)

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_register_new_username_fail(aresponses, new_user_fail_response):
    """Test that a failed new user registration is handled correctly."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/register",
        "post",
        response=aiohttp.web_response.json_response(new_user_fail_response, status=400),
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

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_register_new_username_success(aresponses, new_user_success_response):
    """Test a successful new user registration."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/register",
        "post",
        response=aiohttp.web_response.json_response(
            new_user_success_response, status=200
        ),
    )

    async with aiohttp.ClientSession() as session:
        resp = await Client.async_register_new_username(
            "user", "password", "email@email.com", "My Organization", session=session
        )
        assert resp == {"user": "user", "ok": "User created"}

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_request_password_reset_fail(
    aresponses, login_response, password_reset_fail_response
):
    """Test that a failed password reset request is handled correctly."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/password",
        "get",
        response=aiohttp.web_response.json_response(
            password_reset_fail_response, status=400
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = await Client.async_login("user", "password", session=session)
        with pytest.raises(RequestError) as err:
            await client.async_request_password_reset()
        assert "A problem occurred, your request could not be processed" in str(err)

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_successful_token_refresh(
    aresponses, forbidden_response, realtime_emissions_response, login_response
):
    """Test that a refreshed token works correctly."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/index",
        "get",
        aresponses.Response(
            text=forbidden_response, status=403, headers={"Content-Type": "text/html"},
        ),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/index",
        "get",
        response=aiohttp.web_response.json_response(
            realtime_emissions_response, status=200
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = await Client.async_login(
            "user",
            "password",
            session=session,
            # We set a 0 delay so that this test is unnecessarily slowed down:
            request_retry_delay=0,
        )

        # If we get past here without raising an exception, we know the refresh worked:
        await client.emissions.async_get_realtime_emissions("40.6971494", "-74.2598655")

    aresponses.assert_plan_strictly_followed()
