# 🌎 aiowatttime: an asyncio-based, Python3 library for WattTime emissions data

[![CI][ci-badge]][ci]
[![PyPI][pypi-badge]][pypi]
[![Version][version-badge]][version]
[![License][license-badge]][license]
[![Code Coverage][codecov-badge]][codecov]
[![Maintainability][maintainability-badge]][maintainability]

<a href="https://www.buymeacoffee.com/bachya1208P" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

`aiowatttime` is a Python 3, asyncio-friendly library for interacting with
[WattTime](https://www.watttime.org) emissions data.

- [Python Versions](#python-versions)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

# Python Versions

`aiowatttime` is currently supported on:

- Python 3.10
- Python 3.11
- Python 3.12

# Installation

```bash
pip install aiowatttime
```

# Usage

## Getting an API Key

Simply clone this repo and run the included interactive script:

```bash
$ script/register
```

Note that WattTime offers three plans: Visitors, Analyst, and Pro. The type you use
will determine which elements of this library are available to use. You can read more
details [here][watttime-data-plans].

## Creating and Using a Client

The `Client` is the primary method of interacting with the API:

```python
import asyncio

from aiowatttime import Client


async def main() -> None:
    client = await Client.login("<USERNAME>", "<PASSWORD>")
    # ...


asyncio.run(main())
```

By default, the library creates a new connection to the API with each coroutine. If
you are calling a large number of coroutines (or merely want to squeeze out every second
of runtime savings possible), an [`aiohttp`][aiohttp] `ClientSession` can be used for
connection pooling:

```python
import asyncio

from aiohttp import ClientSession

from aiowatttime import Client


async def main() -> None:
    async with ClientSession() as session:
        client = await Client.login("<USERNAME>", "<PASSWORD>", session=session)
        # ...


asyncio.run(main())
```

## Programmatically Requesting a Password Reset

```python
await client.async_request_password_reset()
```

## Getting Emissions Data

### Grid Region

It may be useful to first get the "grid region" (i.e., geographical info) for the area
you care about:

```python
await client.emissions.async_get_grid_region("<LATITUDE>", "<LONGITUDE>")
# >>> { "id": 263, "abbrev": "PJM_NJ", "name": "PJM New Jersey" }
```

Getting emissions data will require either your latitude/longitude _or_ the "balancing
authority abbreviation" (`PJM_NJ` in the example above).

### Realtime Data

```python
await client.emissions.async_get_realtime_emissions("<LATITUDE>", "<LONGITUDE>")
# >>> { "freq": "300", "ba": "CAISO_NORTH", "percent": "53", "moer": "850.743982", ... }
```

### Forecasted Data

```python
await client.emissions.async_get_forecasted_emissions("<BA_ABBREVATION>")
# >>> [ { "generated_at": "2021-08-05T09:05:00+00:00", "forecast": [...] } ]
```

You can also get the forecasted data using a specific start and end `datetime.datetime`:

```python
from datetime import datetime

await client.emissions.async_get_forecasted_emissions(
    "<BA_ABBREVATION>",
    start_datetime=datetime(2021, 1, 1),
    end_datetime=datetime(2021, 2, 1),
)
# >>> [ { "generated_at": "2021-08-05T09:05:00+00:00", "forecast": [...] } ]
```

### Historical Data

```python
await client.emissions.async_get_historical_emissions("<LATITUDE>", "<LONGITUDE>")
# >>> [ { "point_time": "2019-02-21T00:15:00.000Z", "value": 844, ... } ]
```

You can also get the historical data using a specific start and end `datetime.datetime`:

```python
from datetime import datetime

await client.emissions.async_get_historical_emissions(
    "<LATITUDE>",
    "<LONGITUDE>",
    start_datetime=datetime(2021, 1, 1),
    end_datetime=datetime(2021, 2, 1),
)
# >>> [ { "point_time": "2019-02-21T00:15:00.000Z", "value": 844, ... } ]
```

## Retry Logic

By default, `aiowatttime` will handle expired access tokens for you. When a token expires,
the library will attempt the following sequence 3 times:

- Request a new token
- Pause for 1 second (to be respectful of the API rate limiting)
- Execute the original request again

Both the number of retries and the delay between retries can be configured when
instantiating a client:

```python
import asyncio

from aiohttp import ClientSession

from aiowatttime import Client


async def main() -> None:
    async with ClientSession() as session:
        client = await Client.async_login(
            "user",
            "password",
            session=session,
            # Make 7 retry attempts:
            request_retries=7,
            # Delay 4 seconds between attempts:
            request_retry_delay=4,
        )


asyncio.run(main())
```

As always, an invalid username/password combination will immediately throw an exception.

## Custom Logger

By default, `aiowatttime` provides its own logger. If you should wish to use your own, you
can pass it to the client during instantiation:

```python
import asyncio
import logging

from aiohttp import ClientSession

from aiowatttime import Client

CUSTOM_LOGGER = logging.getLogger("my_custom_logger")


async def main() -> None:
    async with ClientSession() as session:
        client = await Client.async_login(
            "user",
            "password",
            session=session,
            logger=logger,
        )


asyncio.run(main())
```

# Contributing

Thanks to all of [our contributors][contributors] so far!

1. [Check for open features/bugs][issues] or [initiate a discussion on one][new-issue].
2. [Fork the repository][fork].
3. (_optional, but highly recommended_) Create a virtual environment: `python3 -m venv .venv`
4. (_optional, but highly recommended_) Enter the virtual environment: `source ./.venv/bin/activate`
5. Install the dev environment: `script/setup`
6. Code your new feature or bug fix on a new branch.
7. Write tests that cover your new functionality.
8. Run tests and ensure 100% code coverage: `poetry run pytest --cov aiowatttime tests`
9. Update `README.md` with any new documentation.
10. Submit a pull request!

[aiohttp]: https://github.com/aio-libs/aiohttp
[ci-badge]: https://github.com/bachya/aiowatttime/workflows/CI/badge.svg
[ci]: https://github.com/bachya/aiowatttime/actions
[codecov-badge]: https://codecov.io/gh/bachya/aiowatttime/branch/dev/graph/badge.svg
[codecov]: https://codecov.io/gh/bachya/aiowatttime
[contributors]: https://github.com/bachya/aiowatttime/graphs/contributors
[fork]: https://github.com/bachya/aiowatttime/fork
[issues]: https://github.com/bachya/aiowatttime/issues
[license-badge]: https://img.shields.io/pypi/l/aiowatttime.svg
[license]: https://github.com/bachya/aiowatttime/blob/main/LICENSE
[maintainability-badge]: https://api.codeclimate.com/v1/badges/781e64940b1302ae9ac3/maintainability
[maintainability]: https://codeclimate.com/github/bachya/aiowatttime/maintainability
[new-issue]: https://github.com/bachya/aiowatttime/issues/new
[new-issue]: https://github.com/bachya/aiowatttime/issues/new
[pypi-badge]: https://img.shields.io/pypi/v/aiowatttime.svg
[pypi]: https://pypi.python.org/pypi/aiowatttime
[version-badge]: https://img.shields.io/pypi/pyversions/aiowatttime.svg
[version]: https://pypi.python.org/pypi/aiowatttime
[watttime]: https://www.watttime.org
[watttime-data-plans]: https://www.watttime.org/get-the-data/data-plans/
