"""Define common test utilities."""
import os

TEST_PASSWORD = "pass"
TEST_TOKEN = "abcd1234"
TEST_TOKEN_2 = "efgh5678"
TEST_USERNAME = "user"


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()
