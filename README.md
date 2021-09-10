# 🌎 aiowatttime: an asyncio-based, Python3 library for WattTime emissions data

[![CI](https://github.com/bachya/aiowatttime/workflows/CI/badge.svg)](https://github.com/bachya/aiowatttime/actions)
[![PyPi](https://img.shields.io/pypi/v/aiowatttime.svg)](https://pypi.python.org/pypi/aiowatttime)
[![Version](https://img.shields.io/pypi/pyversions/aiowatttime.svg)](https://pypi.python.org/pypi/aiowatttime)
[![License](https://img.shields.io/pypi/l/aiowatttime.svg)](https://github.com/bachya/aiowatttime/blob/master/LICENSE)
[![Code Coverage](https://codecov.io/gh/bachya/aiowatttime/branch/master/graph/badge.svg)](https://codecov.io/gh/bachya/aiowatttime)
[![Maintainability](https://api.codeclimate.com/v1/badges/781e64940b1302ae9ac3/maintainability)](https://codeclimate.com/github/bachya/aiowatttime/maintainability)
[![Say Thanks](https://img.shields.io/badge/SayThanks-!-1EAEDB.svg)](https://saythanks.io/to/bachya)

`aiowatttime` is a Python 3, asyncio-friendly library for interacting with
[WattTime](https://www.watttime.org) emissions data.

- [Python Versions](#python-versions)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

# Python Versions

`aiowatttime` is currently supported on:

* Python 3.8
* Python 3.9

# Installation

```python
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
details here: https://www.watttime.org/get-the-data/data-plans/

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
you are calling a large number of coroutines (or merely want to squeeze out every second of runtime savings possible), an
[`aiohttp`](https://github.com/aio-libs/aiohttp) `ClientSession` can be used for connection
pooling:

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
authority abbreviation" (``PJM_NJ`` in the example above).

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
    "<LONGITUDE>"
    start_datetime=datetime(2021, 1, 1),
    end_datetime=datetime(2021, 2, 1),
)
# >>> [ { "point_time": "2019-02-21T00:15:00.000Z", "value": 844, ... } ]
```

# Contributing

1. [Check for open features/bugs](https://github.com/bachya/aiowatttime/issues)
  or [initiate a discussion on one](https://github.com/bachya/aiowatttime/issues/new).
2. [Fork the repository](https://github.com/bachya/aiowatttime/fork).
3. (_optional, but highly recommended_) Create a virtual environment: `python3 -m venv .venv`
4. (_optional, but highly recommended_) Enter the virtual environment: `source ./venv/bin/activate`
5. Install the dev environment: `script/setup`
6. Code your new feature or bug fix.
7. Write tests that cover your new functionality.
8. Run tests and ensure 100% code coverage: `script/test`
9. Update `README.md` with any new documentation.
10. Add yourself to `AUTHORS.md`.
11. Submit a pull request!
