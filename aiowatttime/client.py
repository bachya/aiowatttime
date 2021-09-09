"""Define an API client."""
from typing import Any, Dict, Optional

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError

from .const import LOGGER
from .errors import RequestError

API_BASE_URL = "https://api2.watttime.org/v2"

DEFAULT_TIMEOUT = 10


class Client:  # pylint: disable=too-few-public-methods
    """Define the client."""

    def __init__(
        self, username: str, password: str, *, session: Optional[ClientSession] = None
    ) -> None:
        """Initialize."""
        self._password = password
        self._session = session
        self._token: Optional[str] = None
        self._username = username

    async def _async_request(
        self, method: str, endpoint: str, **kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make an API request."""
        url = f"{API_BASE_URL}/{endpoint}"

        kwargs.setdefault("headers", {})
        if self._token:
            kwargs["headers"]["Authorization"] = f"Bearer {self._token}"

        use_running_session = self._session and not self._session.closed
        if use_running_session:
            session = self._session
        else:
            session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))

        assert session

        data: Dict[str, Any] = {}

        try:
            async with session.request(method, url, **kwargs) as resp:
                resp.raise_for_status()
                data = await resp.json()
        except ClientError as err:
            raise RequestError(f"Error while requesting {url}: {err}") from err
        finally:
            if not use_running_session:
                await session.close()

        LOGGER.debug("Received data for /%s: %s", endpoint, data)

        return data

    async def async_login(self) -> None:
        """Retrieve and store a new access token."""
        token_resp = await self._async_request("get", "login")
        self._token = token_resp["token"]


async def async_get_client(
    username: str, password: str, *, session: Optional[ClientSession] = None
) -> Client:
    """Get a fully initialized API client."""
    client = Client(username, password, session=session)
    await client.async_login()
    return client
