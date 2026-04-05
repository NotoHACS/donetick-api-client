"""Shared fixtures and utilities for Donetick API client tests."""

from typing import Any

import pytest
import responses

from donetick import DonetickClient


# Constants for testing
TEST_BASE_URL = "http://test.donetick.local:2021"
TEST_TOKEN = "test-jwt-token-12345"


def make_task_data(
    task_id: str = "task-123",
    title: str = "Test Task",
    status: str = "pending",
    **kwargs,
) -> dict:
    """Helper to create task data for mocking."""
    return {
        "id": task_id,
        "title": title,
        "description": kwargs.get("description", "Test description"),
        "due_date": kwargs.get("due_date", "2025-06-01T12:00:00Z"),
        "status": status,
        "priority": kwargs.get("priority", "P2"),
        "labels": kwargs.get("labels", ["test", "important"]),
        "subtasks": kwargs.get("subtasks", []),
        "group_id": kwargs.get("group_id", "group-456"),
        "assignee_id": kwargs.get("assignee_id", "user-789"),
        "created_at": kwargs.get("created_at", "2025-01-01T00:00:00Z"),
        "updated_at": kwargs.get("updated_at", "2025-01-02T00:00:00Z"),
    }


def make_thing_data(
    thing_id: str = "thing-123",
    name: str = "Test Thing",
    thing_type: str = "number",
    value: Any = 42,
    **kwargs,
) -> dict:
    """Helper to create thing data for mocking."""
    return {
        "id": thing_id,
        "name": name,
        "type": thing_type,
        "value": value,
        "group_id": kwargs.get("group_id", "group-456"),
        "created_at": kwargs.get("created_at", "2025-01-01T00:00:00Z"),
    }


@pytest.fixture
def client() -> DonetickClient:
    """Create a DonetickClient instance for testing."""
    return DonetickClient(TEST_BASE_URL, TEST_TOKEN)


@pytest.fixture
def mock_responses() -> Generator[responses.RequestsMock, None, None]:
    """Set up mocked HTTP responses."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture(autouse=True)
def auto_close_client(client: DonetickClient) -> Generator[None, None, None]:
    """Automatically close client after each test."""
    yield
    client.close()
