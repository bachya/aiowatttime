"""Define an API endpoint manager for emissions data."""
from __future__ import annotations

from datetime import datetime
from typing import Awaitable, Callable, TypedDict, cast

DEFAULT_MOER_VERSION = "3.0"


class EmissionForecast(TypedDict):
    """Define a type for an emissions forecast."""

    ba: str
    point_time: str
    value: float
    version: str


class ForecastedEmissionsResponseType(TypedDict):
    """Define a type for a response to async_get_forecasted_emissions."""

    generated_at: str
    forecast: list[EmissionForecast]


class GridRegionResponseType(TypedDict):
    """Define a type for a response to async_get_grid_region."""

    abbrev: str
    id: int
    name: str


class HistoricalEmissionsResponseType(TypedDict):
    """Define a type for a response to async_get_historical_emissions."""

    ba: str
    datatype: str
    frequency: int
    market: str
    point_time: str
    value: float
    version: str


class RealTimeEmissionsResponseType(TypedDict):
    """Define a type for a response to async_get_realtime_emissions."""

    ba: str
    freq: str
    moer: float
    percent: int
    point_time: str


class EmissionsAPI:
    """Define the manager object."""

    def __init__(self, async_request: Callable[..., Awaitable]) -> None:
        """Initialize."""
        self._async_request = async_request

    async def async_get_grid_region(
        self, latitude: str, longitude: str
    ) -> GridRegionResponseType:
        """Return the grid region data for a latitude/longitude."""
        data = await self._async_request(
            "get", "ba-from-loc", params={"latitude": latitude, "longitude": longitude}
        )
        return cast(GridRegionResponseType, data)

    async def async_get_forecasted_emissions(
        self,
        balancing_authority_abbreviation: str,
        *,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> RealTimeEmissionsResponseType:
        """Return the forecasted emissions for a latitude/longitude."""
        if start_datetime and not end_datetime or end_datetime and not start_datetime:
            raise ValueError("You must provided start and end datetimes together")

        params = {"ba": balancing_authority_abbreviation}
        if start_datetime and end_datetime:
            params["starttime"] = start_datetime.isoformat()
            params["endtime"] = end_datetime.isoformat()

        data = await self._async_request("get", "forecast", params=params)
        return cast(RealTimeEmissionsResponseType, data)

    async def async_get_historical_emissions(
        self,
        latitude: str,
        longitude: str,
        *,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        moer_version: str = DEFAULT_MOER_VERSION,
    ) -> HistoricalEmissionsResponseType:
        """Return the historical emissions for a latitude/longitude."""
        if start_datetime and not end_datetime or end_datetime and not start_datetime:
            raise ValueError("You must provided start and end datetimes together")

        params = {"latitude": latitude, "longitude": longitude, "version": moer_version}
        if start_datetime and end_datetime:
            params["starttime"] = start_datetime.isoformat()
            params["endtime"] = end_datetime.isoformat()

        data = await self._async_request("get", "data", params=params)
        return cast(HistoricalEmissionsResponseType, data)

    async def async_get_realtime_emissions(
        self, latitude: str, longitude: str
    ) -> RealTimeEmissionsResponseType:
        """Return the realtime emissions for a latitude/longitude."""
        data = await self._async_request(
            "get", "index", params={"latitude": latitude, "longitude": longitude}
        )
        return cast(RealTimeEmissionsResponseType, data)
