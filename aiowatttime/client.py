"""Define an API client."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, TypedDict, cast

from aiohttp import BasicAuth, ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError, ContentTypeError

from .const import LOGGER
from .emissions import EmissionsAPI
from .errors import InvalidCredentialsError, raise_client_error

API_BASE_URL = "https://api2.watttime.org/v2"

DEFAULT_RETRIES = 3
DEFAULT_RETRY_DELAY = 1
DEFAULT_TIMEOUT = 10


class RegisterNewUserResponseType(TypedDict):
    """Define a type for a response to async_register_new_username."""

    ok: str
    user: str


class TokenResponseType(TypedDict):
    """Define a type for a response to async_authenticate."""

    token: str


class Client:  # pylint: disable=too-many-instance-attributes
    """Define the client."""

    def __init__(
        self,
        *,
        session: ClientSession | None = None,
        logger: logging.Logger = LOGGER,
        request_retry_delay: int = DEFAULT_RETRY_DELAY,
        request_retries: int = DEFAULT_RETRIES,
    ) -> None:
        """Initialize.

        Note that this is not intended to be instantiated directly; instead, users
        should use the async_login and async_register_new_username class methods.
        """
        self._logger = logger
        self._request_retries = request_retries
        self._request_retry_delay = request_retry_delay
        self._session = session

        # Intended to be populated by async_authenticate():
        self._token: str | None = None

        # Intended to be populated by async_login():
        self._password: str | None = None
        self._username: str | None = None

        self.emissions = EmissionsAPI(self._async_request)

    @classmethod
    async def async_login(
        cls,
        username: str,
        password: str,
        *,
        session: ClientSession | None = None,
        logger: logging.Logger = LOGGER,
        request_retry_delay: int = DEFAULT_RETRY_DELAY,
        request_retries: int = DEFAULT_RETRIES,
    ) -> "Client":
        """Get a fully initialized API client."""
        client = cls(
            session=session,
            logger=logger,
            request_retry_delay=request_retry_delay,
            request_retries=request_retries,
        )
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
        logger: logging.Logger = LOGGER,
        request_retry_delay: int = DEFAULT_RETRY_DELAY,
        request_retries: int = DEFAULT_RETRIES,
    ) -> RegisterNewUserResponseType:
        """Get a fully initialized API client."""
        client = cls(
            session=session,
            logger=logger,
            request_retry_delay=request_retry_delay,
            request_retries=request_retries,
        )
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

        use_running_session = self._session and not self._session.closed
        if use_running_session:
            session = self._session
        else:
            session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))

        assert session

        data: dict[str, Any] | list[dict[str, Any]] = {}
        retry = 0

        while retry < self._request_retries:
            if self._token:
                kwargs["headers"]["Authorization"] = f"Bearer {self._token}"
            async with session.request(method, url, **kwargs) as resp:
                try:
                    data = await resp.json()
                except ContentTypeError:
                    # A ContentTypeError is assumed to be a credentials issue (since the
                    # API returns NGINX's default BasicAuth HTML upon 403):
                    if endpoint == "login":
                        # If we are seeing this error upon login, we assume the
                        # username/password are bad:
                        raise InvalidCredentialsError("Invalid credentials") from None

                    # ...otherwise, we assume the token has expired, so we make a few
                    # attempts to refresh it and retry the original request:
                    retry += 1
                    self._logger.debug(
                        "Token failed; trying again (attempt %s of %s)",
                        retry,
                        self._request_retries,
                    )
                    await self.async_authenticate()
                    await asyncio.sleep(self._request_retry_delay)
                    continue

                try:
                    resp.raise_for_status()
                except ClientError as err:
                    assert isinstance(data, dict)
                    raise_client_error(endpoint, data, err)

                break
        else:
            # We only end up here if we continue to have credential issues after
            # several retries:
            raise InvalidCredentialsError("Invalid credentials") from None

        if not use_running_session:
            await session.close()

        self._logger.debug("Received data for /%s: %s", endpoint, data)

        return data

    async def async_authenticate(self) -> None:
        """Retrieve and store a new access token."""
        # Invalidate the token first since we can't have it *and* BasicAuth credentials
        # in the same request:
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
