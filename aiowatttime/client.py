"""Define an API client."""
from __future__ import annotations

from typing import Any, TypedDict, cast

from aiohttp import BasicAuth, ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError, ContentTypeError

from .const import LOGGER
from .emissions import EmissionsAPI
from .errors import raise_error

API_BASE_URL = "https://api2.watttime.org/v2"

DEFAULT_TIMEOUT = 10


class RegisterNewUserResponseType(TypedDict):
    """Define a type for a response to async_register_new_username."""

    ok: str
    user: str


class TokenResponseType(TypedDict):
    """Define a type for a response to async_authenticate."""

    token: str


class Client:
    """Define the client."""

    def __init__(self, *, session: ClientSession | None = None) -> None:
        """Initialize.

        Note that this is not intended to be instantiated directly; instead, users
        should use the async_login and async_register_new_username class methods.
        """
        self._session = session

        # Intended to be populated by async_authenticate():
        self._token: str | None = None

        # Intended to be populated by async_login():
        self._password: str | None = None
        self._username: str | None = None

        self.emissions = EmissionsAPI(self._async_request)

    @classmethod
    async def async_login(
        cls, username: str, password: str, *, session: ClientSession | None = None
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
        session: ClientSession | None = None,
    ) -> RegisterNewUserResponseType:
        """Get a fully initialized API client."""
        client = cls(session=session)
        data = await client._async_request(
            "post",
            "register",
            json={
                "username": username,
                "password": password,
                "email": email,
                "org": organization,
            },
        )
        return cast(RegisterNewUserResponseType, data)

    async def _async_request(
        self, method: str, endpoint: str, **kwargs: dict[str, Any]
    ) -> dict[str, Any] | list[dict[str, Any]]:
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

        data: dict[str, Any] | list[dict[str, Any]] = {}

        try:
            async with session.request(method, url, **kwargs) as resp:
                data = await resp.json()
                resp.raise_for_status()
        except (ClientError, ContentTypeError) as err:
            assert isinstance(data, dict)
            raise_error(endpoint, data, err)
        finally:
            if not use_running_session:
                await session.close()

        LOGGER.debug("Received data for /%s: %s", endpoint, data)

        return data

    async def async_authenticate(self) -> None:
        """Retrieve and store a new access token."""
        self._token = None
        token_resp = cast(
            TokenResponseType,
            await self._async_request(
                "get", "login", auth=BasicAuth(self._username, password=self._password)
            ),
        )
        self._token = token_resp["token"]

    async def async_request_password_reset(self) -> None:
        """Ask the API to send a password reset email."""
        await self._async_request("get", "password")
