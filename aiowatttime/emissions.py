"""Define an API endpoint manager for emissions data."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

DEFAULT_MOER_VERSION = "3.0"


class EmissionsAPI:
    """Define the manager object."""

    def __init__(self, async_request: Callable[..., Awaitable[dict[str, Any]]]) -> None:
        """Initialize.

        Args:
            async_request: The request method from the Client object.
        """
        self._async_request = async_request

    async def async_get_grid_region(
        self, latitude: str, longitude: str, signal_type: str
    ) -> dict[str, Any]:
        """Return the grid region data for a latitude/longitude.

        Args:
            latitude: A latitude.
            longitude: A longitude.
            signal_type: The signal type.

        Returns:
            An API response payload.
        """
        return await self._async_request(
            "get",
            "v3/region-from-loc",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "signal_type": signal_type,
            },
        )

    async def async_get_forecasted_emissions(
        self,
        region: str,
        signal_type: str,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> dict[str, Any]:
        """Return the forecasted emissions for a region.

        Args:
            region: The abbreviated form of a region.
            signal_type: The signal type.
            start_datetime: An optional starting datetime to limit data.
            end_datetime: An optional ending datetime to limit data.

        Returns:
            An API response payload.
        """
        return await self._async_request(
            "get",
            "v3/forecast/historical",
            params={
                "end": end_datetime.isoformat(),
                "region": region,
                "signal_type": signal_type,
                "start": start_datetime.isoformat(),
            },
        )

    async def async_get_historical_emissions(
        self,
        region: str,
        signal_type: str,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> dict[str, Any]:
        """Return the historical emissions for a latitude/longitude.

        Args:
            region: The abbreviated form of a region.
            signal_type: The signal type.
            start_datetime: An optional starting datetime to limit data.
            end_datetime: An optional ending datetime to limit data.

        Returns:
            An API response payload.
        """
        return await self._async_request(
            "get",
            "v3/historical",
            params={
                "end": end_datetime.isoformat(),
                "region": region,
                "signal_type": signal_type,
                "start": start_datetime.isoformat(),
            },
        )

    async def async_get_realtime_emissions(self, region: str) -> dict[str, Any]:
        """Return the realtime emissions for a region.

        Args:
            region: The abbreviated form of a region.

        Returns:
            An API response payload.
        """
        return await self._async_request(
            "get",
            "v3/signal-index",
            params={
                "region": region,
            },
        )
