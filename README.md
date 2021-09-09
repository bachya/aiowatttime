# 🌎 aiowatttime: an asyncio-based, Python3 library for LOOK.in devices

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

* Python 3.6
* Python 3.7
* Python 3.8
* Python 3.9

# Installation

```python
pip install aiowatttime
```

# Usage

## Setup

```python
import asyncio

from aiowatttime import async_get_client


async def main() -> None:
    device = await async_get_client("<USERNAME>", "<PASSWORD>")

    # ...


asyncio.run(main())
```

By default, the library creates a new connection to the device with each coroutine. If
you are calling a large number of coroutines (or merely want to squeeze out every second
of runtime savings possible), an
[`aiohttp`](https://github.com/aio-libs/aiohttp) `ClientSession` can be used for connection
pooling:

```python
import asyncio

from aiohttp import ClientSession

from aiowatttime import async_get_client


async def main() -> None:
    async with ClientSession() as session:
        device = await async_get_client("<USERNAME>", "<PASSWORD>", session=session)

        # ...


asyncio.run(main())
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
