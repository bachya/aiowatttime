"""Define an API endpoint manager for emissions data."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any, cast

DEFAULT_MOER_VERSION = "3.0"


class EmissionsAPI:
    """Define the manager object."""

    def __init__(self, async_request: Callable[..., Awaitable]) -> None:
        """Initialize.

        Args:
            async_request: The request method from the Client object.
        """
        self._async_request = async_request

    async def async_get_grid_region(
        self, latitude: str, longitude: str
    ) -> dict[str, Any]:
        """Return the grid region data for a latitude/longitude.

        Args:
            latitude: A latitude.
            longitude: A longitude.

        Returns:
            An API response payload.
        """
        data = await self._async_request(
            "get", "ba-from-loc", params={"latitude": latitude, "longitude": longitude}
        )
        return cast(dict[str, Any], data)

    async def async_get_forecasted_emissions(
        self,
        balancing_authority_abbreviation: str,
        *,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Return the forecasted emissions for a latitude/longitude.

        Args:
            balancing_authority_abbreviation: The abbreviated form of a balancing
                authority.
            start_datetime: An optional starting datetime to limit data.
            end_datetime: An optional ending datetime to limit data.

        Returns:
            An API response payload.

        Raises:
            ValueError: Raised on incorrect parameters.
        """
        if start_datetime and not end_datetime or end_datetime and not start_datetime:
            raise ValueError("You must provided start and end datetimes together")

        params = {"ba": balancing_authority_abbreviation}
        if start_datetime and end_datetime:
            params["starttime"] = start_datetime.isoformat()
            params["endtime"] = end_datetime.isoformat()

        data = await self._async_request("get", "forecast", params=params)
        return cast(list[dict[str, Any]], data)

    async def async_get_historical_emissions(  # pylint: disable=too-many-arguments
        self,
        latitude: str,
        longitude: str,
        *,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        moer_version: str = DEFAULT_MOER_VERSION,
    ) -> dict[str, Any]:
        """Return the historical emissions for a latitude/longitude.

        Args:
            latitude: A latitude.
            longitude: A longitude.
            start_datetime: An optional starting datetime to limit data.
            end_datetime: An optional ending datetime to limit data.
            moer_version: The MOER version to use.

        Returns:
            An API response payload.

        Raises:
            ValueError: Raised on incorrect parameters.
        """
        if start_datetime and not end_datetime or end_datetime and not start_datetime:
            raise ValueError("You must provided start and end datetimes together")

        params = {"latitude": latitude, "longitude": longitude, "version": moer_version}
        if start_datetime and end_datetime:
            params["starttime"] = start_datetime.isoformat()
            params["endtime"] = end_datetime.isoformat()

        data = await self._async_request("get", "data", params=params)
        return cast(dict[str, Any], data)

    async def async_get_realtime_emissions(
        self, latitude: str, longitude: str
    ) -> dict[str, Any]:
        """Return the realtime emissions for a latitude/longitude.

        Args:
            latitude: A latitude.
            longitude: A longitude.

        Returns:
            An API response payload.
        """
        data = await self._async_request(
            "get", "index", params={"latitude": latitude, "longitude": longitude}
        )
        return cast(dict[str, Any], data)
