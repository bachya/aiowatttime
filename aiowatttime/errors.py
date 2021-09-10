"""Define package exceptions."""
from __future__ import annotations

from typing import Any

from aiohttp.client_exceptions import ContentTypeError


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


def raise_error(endpoint: str, data: dict[str, Any], err: Exception) -> None:
    """Return a wrapped error that has the correct info."""
    if isinstance(err, ContentTypeError):
        # When the API runs into a credentials issue, it returns NGINX's default
        # 403 Forbidden HTML, which is an aiohttp.client_exceptions.ContentTypeError:
        raise InvalidCredentialsError("Invalid credentials") from err

    if "message" in data:
        msg = data["message"]
    elif "error" in data:
        msg = data["error"]

    if "Invalid scope" in msg:
        raise InvalidScopeError(f"Unauthorized to request /{endpoint}")
    raise RequestError(f"Error while requesting /{endpoint}: {msg}") from err
