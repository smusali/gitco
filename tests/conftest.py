"""Pytest configuration and fixtures for GitCo tests."""

# ruff: noqa: F403
from tests.fixtures import *

# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]
