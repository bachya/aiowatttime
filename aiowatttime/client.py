"""Define an API client."""
import json
from typing import Any, Dict, Optional

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError

from .const import LOGGER
from .errors import raise_error

API_BASE_URL = "https://api2.watttime.org/v2"

DEFAULT_TIMEOUT = 10


class Client:
    """Define the client."""

    def __init__(self, *, session: Optional[ClientSession] = None) -> None:
        """Initialize.

        Note that this is not intended to be instantiated directly; instead, users
        should use the async_login and async_register_new_username class methods.
        """
        self._session = session

        # Intended to be populated by async_authenticate():
        self._token: Optional[str] = None

        # Intended to be populated by async_login():
        self._password: Optional[str] = None
        self._username: Optional[str] = None

    @classmethod
    async def async_login(
        cls, username: str, password: str, *, session: Optional[ClientSession] = None
    ) -> "Client":
        """Get a fully initialized API client."""
        client = cls(session=session)
        client._username = username
        client._password = password
        await client.async_authenticate()
        return client

    @classmethod
    async def async_register_new_username(
        cls,
        username: str,
        password: str,
        email: str,
        organization: str,
        *,
        session: Optional[ClientSession] = None,
    ) -> Dict[str, Any]:
        """Get a fully initialized API client."""
        client = cls(session=session)
        return await client.async_request(
            "post",
            "register",
            json={
                "username": username,
                "password": password,
                "email": email,
                "org": organization,
            },
        )

    async def async_authenticate(self) -> None:
        """Retrieve and store a new access token."""
        token_resp = await self.async_request("get", "login")
        self._token = token_resp["token"]

    async def async_request(
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
                data = await resp.json()
                resp.raise_for_status()
        except (ClientError, json.decoder.JSONDecodeError) as err:
            raise_error(endpoint, data, err)
        finally:
            if not use_running_session:
                await session.close()

        LOGGER.debug("Received data for /%s: %s", endpoint, data)

        return data

    async def async_request_password_reset(self) -> None:
        """Ask the API to send a password reset email."""
        await self.async_request("get", "password")
