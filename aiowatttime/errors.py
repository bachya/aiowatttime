"""Define package exceptions."""
from __future__ import annotations

from typing import Any


class WattTimeError(Exception):
    """Define a base exception."""

    pass


class InvalidCredentialsError(WattTimeError):
    """Define an error related to invalid credentials."""

    pass


class InvalidScopeError(WattTimeError):
    """Define an error related to requesting a resource for which we aren't scope."""

    pass


class RequestError(WattTimeError):
    """Define an error related to a bad HTTP request."""

    pass


class UsernameTakenError(WattTimeError):
    """Define an error related a username already being registered."""

    pass


ERROR_MESSAGE_TO_EXCEPTION_MAP = {
    "Invalid scope": InvalidScopeError,
    "That username is taken": UsernameTakenError,
}


def raise_client_error(endpoint: str, data: dict[str, Any], err: Exception) -> None:
    """Wrap an aiohttp.exceptions.ClientError in the correct exception type."""
    if "message" in data:
        msg = data["message"]
    elif "error" in data:
        msg = data["error"]

    try:
        [exception] = [v for k, v in ERROR_MESSAGE_TO_EXCEPTION_MAP.items() if k in msg]
    except ValueError:
        exception = RequestError

    raise exception(f"Error while requesting /{endpoint}: {msg}") from err
