"""Tests for Donetick API task endpoints."""

import pytest
import responses

from donetick import (
    DonetickClient,
    DonetickNotFoundError,
    DonetickValidationError,
)
from donetick.models import Task, TaskCreate, TaskUpdate, Subtask

from .conftest import TEST_BASE_URL, make_task_data


class TestListTasks:
    """Tests for list_tasks endpoint."""

    @responses.activate
    def test_list_tasks_basic(self, client: DonetickClient) -> None:
        """Test basic task listing without filters."""
        tasks_data = [
            make_task_data("task-1", "First Task"),
            make_task_data("task-2", "Second Task"),
        ]
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/tasks",
            json=tasks_data,
            status=200,
        )

        tasks = client.list_tasks()

        assert len(tasks) == 2
        assert all(isinstance(t, Task) for t in tasks)
        assert tasks[0].title == "First Task"
        assert tasks[1].title == "Second Task"

    @responses.activate
    def test_list_tasks_with_status_filter(self, client: DonetickClient) -> None:
        """Test listing tasks with status filter."""
        tasks_data = [make_task_data("task-1", "Pending Task", status="pending")]
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/tasks",
            json=tasks_data,
            status=200,
        )

        tasks = client.list_tasks(status="pending")

        assert len(tasks) == 1
        assert tasks[0].status == "pending"

    @responses.activate
    def test_list_tasks_with_group_filter(self, client: DonetickClient) -> None:
        """Test listing tasks with group_id filter."""
        tasks_data = [make_task_data("task-1", "Group Task", group_id="group-abc")]
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/tasks",
            json=tasks_data,
            status=200,
        )

        tasks = client.list_tasks(group_id="group-abc")

        assert len(tasks) == 1
        assert tasks[0].group_id == "group-abc"

    @responses.activate
    def test_list_tasks_with_assignee_filter(self, client: DonetickClient) -> None:
        """Test listing tasks with assignee_id filter."""
        tasks_data = [make_task_data("task-1", "Assigned Task", assignee_id="user-xyz")]
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/tasks",
            json=tasks_data,
            status=200,
        )

        tasks = client.list_tasks(assignee_id="user-xyz")

        assert len(tasks) == 1
        assert tasks[0].assignee_id == "user-xyz"

    @responses.activate
    def test_list_tasks_with_pagination(self, client: DonetickClient) -> None:
        """Test listing tasks with limit and offset."""
        tasks_data = [make_task_data("task-3", "Third Task")]
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/tasks",
            json=tasks_data,
            status=200,
        )

        tasks = client.list_tasks(limit=10, offset=20)

        assert len(tasks) == 1
        request = responses.calls[0].request
        assert "limit=10" in request.url
        assert "offset=20" in request.url

    @responses.activate
    def test_list_tasks_empty_response(self, client: DonetickClient) -> None:
        """Test listing tasks with empty response."""
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/tasks",
            json=[],
            status=200,
        )

        tasks = client.list_tasks()

        assert tasks == []

    @responses.activate
    def test_list_tasks_all_filters_combined(self, client: DonetickClient) -> None:
        """Test listing tasks with all filters combined."""
        tasks_data = [make_task_data("task-1", "Filtered Task")]
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/tasks",
            json=tasks_data,
            status=200,
        )

        tasks = client.list_tasks(
            status="pending",
            group_id="group-1",
            assignee_id="user-1",
            limit=25,
            offset=10,
        )

        assert len(tasks) == 1
        request = responses.calls[0].request
        assert "status=pending" in request.url
        assert "group_id=group-1" in request.url
        assert "assignee_id=user-1" in request.url
        assert "limit=25" in request.url
        assert "offset=10" in request.url


class TestGetTask:
    """Tests for get_task endpoint."""

    @responses.activate
    def test_get_task_success(self, client: DonetickClient) -> None:
        """Test getting a task by valid ID."""
        task_data = make_task_data("task-abc", "Specific Task")
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/tasks/task-abc",
            json=task_data,
            status=200,
        )

        task = client.get_task("task-abc")

        assert isinstance(task, Task)
        assert task.id == "task-abc"
        assert task.title == "Specific Task"

    @responses.activate
    def test_get_task_not_found(self, client: DonetickClient) -> None:
        """Test getting a non-existent task."""
        responses.add(
            responses.GET,
            f"{TEST_BASE_URL}/api/v1/tasks/nonexistent",
            json={"error": "Task not found"},
            status=404,
        )

        with pytest.raises(DonetickNotFoundError):
            client.get_task("nonexistent")


class TestCreateTask:
    """Tests for create_task endpoint."""

    @responses.activate
    def test_create_task_minimal(self, client: DonetickClient) -> None:
        """Test creating a task with minimal data."""
        task_create = TaskCreate(title="New Task")
        response_data = make_task_data("new-task-1", "New Task")
        responses.add(
            responses.POST,
            f"{TEST_BASE_URL}/api/v1/tasks",
            json=response_data,
            status=201,
        )

        task = client.create_task(task_create)

        assert isinstance(task, Task)
        assert task.title == "New Task"
        request = responses.calls[0].request
        assert b'"title":"New Task"' in request.body

    @responses.activate
    def test_create_task_full(self, client: DonetickClient) -> None:
        """Test creating a task with all fields."""
        task_create = TaskCreate(
            title="Complete Task",
            description="A full description",
            recurrence="weekly",
            priority="P1",
            labels=["urgent", "work"],
            subtasks=[Subtask(title="Step 1"), Subtask(title="Step 2", completed=True)],
            group_id="group-123",
            assignee_id="user-456",
        )
        response_data = make_task_data(
            "full-task-1",
            "Complete Task",
            description="A full description",
            priority="P1",
            labels=["urgent", "work"],
        )
        responses.add(
            responses.POST,
            f"{TEST_BASE_URL}/api/v1/tasks",
            json=response_data,
            status=201,
        )

        task = client.create_task(task_create)

        assert task.title == "Complete Task"

    @responses.activate
    def test_create_task_validation_error(self, client: DonetickClient) -> None:
        """Test creating a task with invalid data."""
        task_create = TaskCreate(title="Invalid")
        responses.add(
            responses.POST,
            f"{TEST_BASE_URL}/api/v1/tasks",
            json={"error": "Invalid due_date format"},
            status=400,
        )

        with pytest.raises(DonetickValidationError):
            client.create_task(task_create)


class TestUpdateTask:
    """Tests for update_task endpoint."""

    @responses.activate
    def test_update_task_partial(self, client: DonetickClient) -> None:
        """Test partial task update."""
        task_update = TaskUpdate(title="Updated Title")
        response_data = make_task_data("task-1", "Updated Title")
        responses.add(
            responses.PUT,
            f"{TEST_BASE_URL}/api/v1/tasks/task-1",
            json=response_data,
            status=200,
        )

        task = client.update_task("task-1", task_update)

        assert task.title == "Updated Title"

    @responses.activate
    def test_update_task_full(self, client: DonetickClient) -> None:
        """Test full task update."""
        task_update = TaskUpdate(
            title="Fully Updated",
            description="New description",
            priority="P3",
            labels=["updated"],
        )
        response_data = make_task_data(
            "task-1",
            "Fully Updated",
            description="New description",
            priority="P3",
            labels=["updated"],
        )
        responses.add(
            responses.PUT,
            f"{TEST_BASE_URL}/api/v1/tasks/task-1",
            json=response_data,
            status=200,
        )

        task = client.update_task("task-1", task_update)

        assert task.title == "Fully Updated"
        assert task.description == "New description"

    @responses.activate
    def test_update_task_not_found(self, client: DonetickClient) -> None:
        """Test updating non-existent task."""
        task_update = TaskUpdate(title="Ghost Task")
        responses.add(
            responses.PUT,
            f"{TEST_BASE_URL}/api/v1/tasks/missing",
            json={"error": "Task not found"},
            status=404,
        )

        with pytest.raises(DonetickNotFoundError):
            client.update_task("missing", task_update)


class TestCompleteTask:
    """Tests for complete_task endpoint."""

    @responses.activate
    def test_complete_task_success(self, client: DonetickClient) -> None:
        """Test marking task as complete."""
        responses.add(
            responses.POST,
            f"{TEST_BASE_URL}/api/v1/tasks/task-1/complete",
            json={"status": "completed", "completed_at": "2025-01-15T10:00:00Z"},
            status=200,
        )

        result = client.complete_task("task-1")

        assert result["status"] == "completed"

    @responses.activate
    def test_complete_task_already_complete(self, client: DonetickClient) -> None:
        """Test completing already completed task."""
        responses.add(
            responses.POST,
            f"{TEST_BASE_URL}/api/v1/tasks/task-1/complete",
            json={"status": "already_completed"},
            status=200,
        )

        result = client.complete_task("task-1")

        assert "status" in result

    @responses.activate
    def test_complete_task_not_found(self, client: DonetickClient) -> None:
        """Test completing non-existent task."""
        responses.add(
            responses.POST,
            f"{TEST_BASE_URL}/api/v1/tasks/missing/complete",
            json={"error": "Task not found"},
            status=404,
        )

        with pytest.raises(DonetickNotFoundError):
            client.complete_task("missing")


class TestDeleteTask:
    """Tests for delete_task endpoint."""

    @responses.activate
    def test_delete_task_success(self, client: DonetickClient) -> None:
        """Test deleting a task."""
        responses.add(
            responses.DELETE,
            f"{TEST_BASE_URL}/api/v1/tasks/task-1",
            status=204,
        )

        result = client.delete_task("task-1")

        assert result is None

    @responses.activate
    def test_delete_task_not_found(self, client: DonetickClient) -> None:
        """Test deleting non-existent task."""
        responses.add(
            responses.DELETE,
            f"{TEST_BASE_URL}/api/v1/tasks/missing",
            json={"error": "Task not found"},
            status=404,
        )

        with pytest.raises(DonetickNotFoundError):
            client.delete_task("missing")

    @responses.activate
    def test_delete_task_already_deleted(self, client: DonetickClient) -> None:
        """Test deleting already deleted task."""
        responses.add(
            responses.DELETE,
            f"{TEST_BASE_URL}/api/v1/tasks/already-deleted",
            json={"error": "Task not found"},
            status=404,
        )

        with pytest.raises(DonetickNotFoundError):
            client.delete_task("already-deleted")
