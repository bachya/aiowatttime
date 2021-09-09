"""Define package exceptions."""


class WattTimeError(Exception):
    """Define a base exception."""

    pass


class RequestError(WattTimeError):
    """Define an error related a bad HTTP request."""

    pass
