"""Define tests for the emissions API endpoints."""
# pylint: disable=protected-access
from datetime import datetime

import aiohttp
import pytest

from aiowatttime import Client
from aiowatttime.errors import CoordinatesNotFoundError, InvalidScopeError


@pytest.mark.asyncio
async def test_coordinates_not_found(
    aresponses, coordinates_not_found_response, login_response
):
    """Test that unknown coordinates are handled correctly."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/ba-from-loc",
        "get",
        response=aiohttp.web_response.json_response(
            coordinates_not_found_response, status=404
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = await Client.async_login("user", "password", session=session)
        with pytest.raises(CoordinatesNotFoundError) as err:
            await client.emissions.async_get_grid_region("0", "0")
        assert "Coordinates not found" in str(err)


@pytest.mark.asyncio
async def test_get_grid_region(aresponses, grid_region_response, login_response):
    """Test getting grid region data for a latitude/longitude."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/ba-from-loc",
        "get",
        response=aiohttp.web_response.json_response(grid_region_response, status=200),
    )

    async with aiohttp.ClientSession() as session:
        client = await Client.async_login("user", "password", session=session)
        region_data = await client.emissions.async_get_grid_region(
            "40.6971494", "-74.2598655"
        )
        assert region_data == {"id": 263, "abbrev": "PJM_NJ", "name": "PJM New Jersey"}


@pytest.mark.asyncio
async def test_get_forecasted_emissions(
    aresponses, forecasted_emissions_response, login_response
):
    """Test getting forecasted emissions data for a balancing authority."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/forecast",
        "get",
        response=aiohttp.web_response.json_response(
            forecasted_emissions_response, status=200
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = await Client.async_login("user", "password", session=session)

        with pytest.raises(ValueError):
            # Test having only one datetime kwarg:
            forecast_data = await client.emissions.async_get_forecasted_emissions(
                "NYISO_NYC",
                start_datetime=datetime(2021, 1, 1),
            )

        forecast_data = await client.emissions.async_get_forecasted_emissions(
            "NYISO_NYC",
            start_datetime=datetime(2021, 1, 1),
            end_datetime=datetime(2021, 2, 1),
        )
        assert len(forecast_data[0]["forecast"]) == 2


@pytest.mark.asyncio
async def test_get_historical_emissions(
    aresponses, historical_emissions_response, login_response
):
    """Test getting historical emissions data for a latitude/longitude."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/data",
        "get",
        response=aiohttp.web_response.json_response(
            historical_emissions_response, status=200
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = await Client.async_login("user", "password", session=session)

        with pytest.raises(ValueError):
            # Test having only one datetime kwarg:
            historical_data = await client.emissions.async_get_historical_emissions(
                "40.6971494",
                "-74.2598655",
                start_datetime=datetime(2021, 1, 1),
            )

        historical_data = await client.emissions.async_get_historical_emissions(
            "40.6971494",
            "-74.2598655",
            start_datetime=datetime(2021, 3, 1),
            end_datetime=datetime(2021, 3, 31),
        )
        assert len(historical_data) == 4


@pytest.mark.asyncio
async def test_get_realtime_emissions(
    aresponses, realtime_emissions_response, login_response
):
    """Test getting realtime emissions data for a latitude/longitude."""
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
        client = await Client.async_login("user", "password", session=session)
        realtime_data = await client.emissions.async_get_realtime_emissions(
            "40.6971494", "-74.2598655"
        )
        assert realtime_data["percent"] == "53"


@pytest.mark.asyncio
async def test_invalid_scope(aresponses, invalid_scope_response, login_response):
    """Test that a request to an invalid scope is handled correctly."""
    aresponses.add(
        "api2.watttime.org",
        "/v2/login",
        "get",
        response=aiohttp.web_response.json_response(login_response, status=200),
    )
    aresponses.add(
        "api2.watttime.org",
        "/v2/forecast",
        "get",
        response=aiohttp.web_response.json_response(invalid_scope_response, status=403),
    )

    async with aiohttp.ClientSession() as session:
        client = await Client.async_login("user", "password", session=session)

        with pytest.raises(InvalidScopeError):
            await client.emissions.async_get_forecasted_emissions(
                "NYISO_NYC",
                start_datetime=datetime(2021, 1, 1),
                end_datetime=datetime(2021, 2, 1),
            )
