"""Tests for Donetick API things endpoints."""

import pytest
import responses

from donetick import (
    DonetickClient,
    DonetickNotFoundError,
)
from donetick.models import Thing

from .conftest import TEST_BASE_URL, make_thing_data


class TestListThings:
    """Tests for list_things endpoint."""

    @responses.activate
    def test_list_things_success(self, client: DonetickClient) -> None:
        """Test listing all things."""
        things_data = [
            make_thing_data("thing-1", "Counter Thing", "number", 42),
            make_thing_data("thing-2", "Flag Thing", "boolean", True),
            make_thing_data("thing-3", "Note Thing", "text", "Hello World"),
        ]
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/things",
            json=things_data,
            status=200,
        )

        things = client.list_things()

        assert len(things) == 3
        assert all(isinstance(t, Thing) for t in things)
        assert things[0].name == "Counter Thing"
        assert things[0].type == "number"
        assert things[0].value == 42
        assert things[1].type == "boolean"
        assert things[1].value is True
        assert things[2].type == "text"
        assert things[2].value == "Hello World"

    @responses.activate
    def test_list_things_empty(self, client: DonetickClient) -> None:
        """Test listing things when none exist."""
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/things",
            json=[],
            status=200,
        )

        things = client.list_things()

        assert things == []

    @responses.activate
    def test_list_things_single_item(self, client: DonetickClient) -> None:
        """Test listing things with single item."""
        things_data = [make_thing_data("thing-1", "Only Thing", "number", 0)]
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/things",
            json=things_data,
            status=200,
        )

        things = client.list_things()

        assert len(things) == 1
        assert things[0].name == "Only Thing"


class TestGetThing:
    """Tests for get_thing endpoint."""

    @responses.activate
    def test_get_thing_success(self, client: DonetickClient) -> None:
        """Test getting a thing by ID."""
        thing_data = make_thing_data("thing-abc", "Specific Thing", "number", 100)
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/things/thing-abc",
            json=thing_data,
            status=200,
        )

        thing = client.get_thing("thing-abc")

        assert isinstance(thing, Thing)
        assert thing.id == "thing-abc"
        assert thing.name == "Specific Thing"
        assert thing.value == 100

    @responses.activate
    def test_get_thing_boolean_type(self, client: DonetickClient) -> None:
        """Test getting a boolean-type thing."""
        thing_data = make_thing_data("thing-flag", "Enabled Flag", "boolean", False)
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/things/thing-flag",
            json=thing_data,
            status=200,
        )

        thing = client.get_thing("thing-flag")

        assert thing.type == "boolean"
        assert thing.value is False

    @responses.activate
    def test_get_thing_text_type(self, client: DonetickClient) -> None:
        """Test getting a text-type thing."""
        thing_data = make_thing_data(
            "thing-note", "Status Note", "text", "System operational"
        )
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/things/thing-note",
            json=thing_data,
            status=200,
        )

        thing = client.get_thing("thing-note")

        assert thing.type == "text"
        assert thing.value == "System operational"

    @responses.activate
    def test_get_thing_with_null_group(self, client: DonetickClient) -> None:
        """Test getting a thing with no group_id."""
        thing_data = make_thing_data("thing-solo", "Solo Thing", "number", 1)
        thing_data["group_id"] = None
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/things/thing-solo",
            json=thing_data,
            status=200,
        )

        thing = client.get_thing("thing-solo")

        assert thing.group_id is None

    @responses.activate
    def test_get_thing_not_found(self, client: DonetickClient) -> None:
        """Test getting non-existent thing."""
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/things/nonexistent",
            json={"error": "Thing not found"},
            status=404,
        )

        with pytest.raises(DonetickNotFoundError):
            client.get_thing("nonexistent")

    @responses.activate
    def test_get_thing_complex_value(self, client: DonetickClient) -> None:
        """Test getting thing with complex/nested value."""
        thing_data = make_thing_data(
            "thing-complex",
            "Complex Thing",
            "json",
            {"nested": {"key": "value"}, "array": [1, 2, 3]},
        )
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/things/thing-complex",
            json=thing_data,
            status=200,
        )

        thing = client.get_thing("thing-complex")

        assert thing.value == {"nested": {"key": "value"}, "array": [1, 2, 3]}


class TestThingsEdgeCases:
    """Edge case tests for things endpoints."""

    @responses.activate
    def test_thing_with_zero_value(self, client: DonetickClient) -> None:
        """Test thing with zero as value."""
        thing_data = make_thing_data("thing-zero", "Zero Counter", "number", 0)
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/things/thing-zero",
            json=thing_data,
            status=200,
        )

        thing = client.get_thing("thing-zero")

        assert thing.value == 0

    @responses.activate
    def test_thing_with_empty_string(self, client: DonetickClient) -> None:
        """Test thing with empty string value."""
        thing_data = make_thing_data("thing-empty", "Empty Note", "text", "")
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/things/thing-empty",
            json=thing_data,
            status=200,
        )

        thing = client.get_thing("thing-empty")

        assert thing.value == ""

    @responses.activate
    def test_thing_with_float_value(self, client: DonetickClient) -> None:
        """Test thing with float value."""
        thing_data = make_thing_data("thing-float", "Temperature", "number", 23.5)
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/things/thing-float",
            json=thing_data,
            status=200,
        )

        thing = client.get_thing("thing-float")

        assert thing.value == 23.5

    @responses.activate
    def test_thing_with_negative_value(self, client: DonetickClient) -> None:
        """Test thing with negative value."""
        thing_data = make_thing_data("thing-neg", "Temperature", "number", -10)
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/things/thing-neg",
            json=thing_data,
            status=200,
        )

        thing = client.get_thing("thing-neg")

        assert thing.value == -10
