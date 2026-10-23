"""Shared pytest fixtures."""

import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.storage import store


@pytest.fixture
def client():
    store.clear()
    with TestClient(app) as test_client:
        yield test_client
    store.clear()
