"""Run an example script to quickly test."""

import asyncio
import logging

from aiohttp import ClientSession

from aiowatttime import Client
from aiowatttime.errors import WattTimeError

_LOGGER = logging.getLogger()

USERNAME = "<USERNAME>"
PASSWORD = "<PASSWORD>"  # noqa: S105

REGION = "PSCO"


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.INFO)
    async with ClientSession() as session:
        try:
            client = await Client.async_login(USERNAME, PASSWORD, session=session)
            realtime_data = await client.emissions.async_get_realtime_emissions(REGION)
            _LOGGER.info(realtime_data)
        except WattTimeError as err:
            _LOGGER.error("There was an error: %s", err)


asyncio.run(main())
