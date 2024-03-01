"""Define tests for the emissions API endpoints."""

from datetime import datetime
from typing import Any

import aiohttp
import pytest
from aresponses import ResponsesMockServer

from aiowatttime import Client
from aiowatttime.errors import CoordinatesNotFoundError, InvalidScopeError


@pytest.mark.asyncio
async def test_coordinates_not_found(
    aresponses: ResponsesMockServer,
    authenticated_watttime_api_server: ResponsesMockServer,
    coordinates_not_found_response: dict[str, Any],
) -> None:
    """Test that unknown coordinates are handled correctly.

    Args:
        aresponses: An aresponses server.
        authenticated_watttime_api_server: A mocked authenticated WattTime API server.
        coordinates_not_found_response: An API response payload.
    """
    async with authenticated_watttime_api_server:
        authenticated_watttime_api_server.add(
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

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_get_grid_region(
    aresponses: ResponsesMockServer,
    authenticated_watttime_api_server: ResponsesMockServer,
    grid_region_response: dict[str, Any],
) -> None:
    """Test getting grid region data for a latitude/longitude.

    Args:
        aresponses: An aresponses server.
        authenticated_watttime_api_server: A mocked authenticated WattTime API server.
        grid_region_response: An API response payload.
    """
    async with authenticated_watttime_api_server:
        authenticated_watttime_api_server.add(
            "api2.watttime.org",
            "/v2/ba-from-loc",
            "get",
            response=aiohttp.web_response.json_response(
                grid_region_response, status=200
            ),
        )

        async with aiohttp.ClientSession() as session:
            client = await Client.async_login("user", "password", session=session)
            region_data = await client.emissions.async_get_grid_region(
                "40.6971494", "-74.2598655"
            )
            assert region_data == {
                "id": 263,
                "abbrev": "PJM_NJ",
                "name": "PJM New Jersey",
            }

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_get_forecasted_emissions(
    aresponses: ResponsesMockServer,
    authenticated_watttime_api_server: ResponsesMockServer,
    forecasted_emissions_response: dict[str, Any],
) -> None:
    """Test getting forecasted emissions data for a balancing authority.

    Args:
        aresponses: An aresponses server.
        authenticated_watttime_api_server: A mocked authenticated WattTime API server.
        forecasted_emissions_response: An API response payload.
    """
    async with authenticated_watttime_api_server:
        authenticated_watttime_api_server.add(
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

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_get_historical_emissions(
    aresponses: ResponsesMockServer,
    authenticated_watttime_api_server: ResponsesMockServer,
    historical_emissions_response: dict[str, Any],
) -> None:
    """Test getting historical emissions data for a latitude/longitude.

    Args:
        aresponses: An aresponses server.
        authenticated_watttime_api_server: A mocked authenticated WattTime API server.
        historical_emissions_response: An API response payload.
    """
    async with authenticated_watttime_api_server:
        authenticated_watttime_api_server.add(
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

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_get_realtime_emissions(
    aresponses: ResponsesMockServer,
    authenticated_watttime_api_server: ResponsesMockServer,
    realtime_emissions_response: dict[str, Any],
) -> None:
    """Test getting realtime emissions data for a latitude/longitude.

    Args:
        aresponses: An aresponses server.
        authenticated_watttime_api_server: A mocked authenticated WattTime API server.
        realtime_emissions_response: An API response payload.
    """
    async with authenticated_watttime_api_server:
        authenticated_watttime_api_server.add(
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

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_invalid_scope(
    aresponses: ResponsesMockServer,
    authenticated_watttime_api_server: ResponsesMockServer,
    invalid_scope_response: dict[str, Any],
) -> None:
    """Test that a request to an invalid scope is handled correctly.

    Args:
        aresponses: An aresponses server.
        authenticated_watttime_api_server: A mocked authenticated WattTime API server.
        invalid_scope_response: An API response payload.
    """
    async with authenticated_watttime_api_server:
        authenticated_watttime_api_server.add(
            "api2.watttime.org",
            "/v2/forecast",
            "get",
            response=aiohttp.web_response.json_response(
                invalid_scope_response, status=403
            ),
        )

        async with aiohttp.ClientSession() as session:
            client = await Client.async_login("user", "password", session=session)

            with pytest.raises(InvalidScopeError):
                await client.emissions.async_get_forecasted_emissions(
                    "NYISO_NYC",
                    start_datetime=datetime(2021, 1, 1),
                    end_datetime=datetime(2021, 2, 1),
                )

    aresponses.assert_plan_strictly_followed()
