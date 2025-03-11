import pytest
from starlette.testclient import TestClient

from pos.runner.setup import setup


@pytest.fixture
def http() -> TestClient:
    return TestClient(setup())
