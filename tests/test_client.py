"""Define tests for the client."""
# pylint: disable=protected-access
import json

import aiohttp
import pytest

from aiowatttime import async_get_client
from aiowatttime.errors import RequestError

from .common import TEST_PASSWORD, TEST_TOKEN, TEST_TOKEN_2, TEST_USERNAME


@pytest.mark.asyncio
async def test_api_error(aresponses):
    """Test the API returning a non-2xx HTTP code."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        aresponses.Response(
            text="Forbidden",
            status=403,
            headers={"Content-Type": "application/json; charset=utf-8"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        with pytest.raises(RequestError):
            await async_get_client(TEST_USERNAME, TEST_PASSWORD, session=session)


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
        client = await async_get_client(TEST_USERNAME, TEST_PASSWORD, session=session)
        assert client._token == TEST_TOKEN


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

    client = await async_get_client(TEST_USERNAME, TEST_PASSWORD)
    assert client._token == TEST_TOKEN


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

    login_response = {"token": TEST_TOKEN_2}

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
        client = await async_get_client(TEST_USERNAME, TEST_PASSWORD, session=session)
        assert client._token == TEST_TOKEN
        await client.async_login()
        assert client._token == TEST_TOKEN_2
