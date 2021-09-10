"""Define package exceptions."""
from typing import Any, Dict


class WattTimeError(Exception):
    """Define a base exception."""

    pass


class RequestError(WattTimeError):
    """Define an error related a bad HTTP request."""

    pass


def raise_error(endpoint: str, data: Dict[str, Any], err: Exception) -> None:
    """Return a wrapped error that has the correct info."""
    if "error" in data:
        msg = data["error"]
    else:
        msg = str(err)
    raise RequestError(f"Error while requesting /{endpoint}: {msg}") from err
