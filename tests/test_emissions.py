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
            "api.watttime.org",
            "/v3/region-from-loc",
            "get",
            response=aiohttp.web_response.json_response(
                coordinates_not_found_response, status=404
            ),
        )

        async with aiohttp.ClientSession() as session:
            client = await Client.async_login("user", "password", session=session)
            with pytest.raises(CoordinatesNotFoundError) as err:
                await client.emissions.async_get_grid_region("0", "0", "co2_moer")
            assert "No coverage available" in str(err)

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
            "api.watttime.org",
            "/v3/region-from-loc",
            "get",
            response=aiohttp.web_response.json_response(
                grid_region_response, status=200
            ),
        )

        async with aiohttp.ClientSession() as session:
            client = await Client.async_login("user", "password", session=session)
            region_data = await client.emissions.async_get_grid_region(
                "40.6971494", "-74.2598655", "co2_moer"
            )
            assert region_data == {
                "region": "PSCO",
                "region_full_name": "Public Service Co of Colorado",
                "signal_type": "co2_moer",
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
            "api.watttime.org",
            "/v3/forecast/historical",
            "get",
            response=aiohttp.web_response.json_response(
                forecasted_emissions_response, status=200
            ),
        )

        async with aiohttp.ClientSession() as session:
            client = await Client.async_login("user", "password", session=session)
            forecast_data = await client.emissions.async_get_forecasted_emissions(
                "PSCO", "co2_moer", datetime(2021, 1, 1), datetime(2021, 1, 31)
            )
            assert forecast_data == {
                "data": [
                    {
                        "generated_at": "2022-07-15T00:00:00+00:00",
                        "forecast": [
                            {"point_time": "2022-07-15T00:00:00+00:00", "value": 870},
                            {"point_time": "2022-07-15T00:05:00+00:00", "value": 870},
                            {"point_time": "2022-07-15T00:10:00+00:00", "value": 870},
                        ],
                    }
                ],
                "meta": {
                    "data_point_period_seconds": 300,
                    "region": "CAISO_NORTH",
                    "warnings": [
                        {
                            "type": "EXAMPLE_WARNING",
                            "message": "This is just an example",
                        }
                    ],
                    "signal_type": "co2_moer",
                    "model": {"date": "2023-03-01"},
                    "units": "lbs_co2_per_mwh",
                    "generated_at_period_seconds": 300,
                },
            }

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
            "api.watttime.org",
            "/v3/historical",
            "get",
            response=aiohttp.web_response.json_response(
                historical_emissions_response, status=200
            ),
        )

        async with aiohttp.ClientSession() as session:
            client = await Client.async_login("user", "password", session=session)
            historical_data = await client.emissions.async_get_historical_emissions(
                "PSCO", "c02_moer", datetime(2021, 3, 1), datetime(2021, 3, 31)
            )
            assert len(historical_data) == 2

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
            "api.watttime.org",
            "/v3/signal-index",
            "get",
            response=aiohttp.web_response.json_response(
                realtime_emissions_response, status=200
            ),
        )

        async with aiohttp.ClientSession() as session:
            client = await Client.async_login("user", "password", session=session)
            realtime_data = await client.emissions.async_get_realtime_emissions("PSCO")
            assert realtime_data == {
                "data": [{"point_time": "2024-06-18T18:40:00+00:00", "value": 96.0}],
                "meta": {
                    "data_point_period_seconds": 300,
                    "region": "PSCO",
                    "signal_type": "co2_moer",
                    "units": "percentile",
                    "warnings": [],
                    "model": {"date": "2022-10-01"},
                },
            }

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
            "api.watttime.org",
            "/v3/forecast/historical",
            "get",
            response=aiohttp.web_response.json_response(
                invalid_scope_response, status=403
            ),
        )

        async with aiohttp.ClientSession() as session:
            client = await Client.async_login("user", "password", session=session)

            with pytest.raises(InvalidScopeError):
                await client.emissions.async_get_forecasted_emissions(
                    "PSCO", "c02_moer", datetime(2021, 1, 1), datetime(2021, 2, 1)
                )

    aresponses.assert_plan_strictly_followed()
