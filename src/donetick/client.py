"""Main Donetick API client."""

from typing import Any, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .exceptions import (
    DonetickAuthError,
    DonetickError,
    DonetickNotFoundError,
    DonetickValidationError,
)
from .models import Task, TaskCreate, TaskUpdate, Thing


class DonetickClient:
    """Client for interacting with Donetick API.
    
    Args:
        base_url: URL of your Donetick instance (e.g., http://10.0.0.100:2021)
        token: JWT authentication token
        timeout: Request timeout in seconds (default: 30)
    
    Example:
        >>> client = DonetickClient("http://10.0.0.100:2021", "your-token")
        >>> tasks = client.list_tasks()
        >>> for task in tasks:
        ...     print(task.title)
    """
    
    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self._client = httpx.Client(
            base_url=f"{self.base_url}/api/v1",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            timeout=timeout,
        )
    
    def _handle_error(self, response: httpx.Response) -> None:
        """Convert HTTP errors to Donetick exceptions."""
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise DonetickAuthError("Invalid or expired token") from e
            elif e.response.status_code == 404:
                raise DonetickNotFoundError(f"Resource not found: {e.response.url}") from e
            elif e.response.status_code == 400:
                raise DonetickValidationError(f"Validation error: {e.response.text}") from e
            else:
                raise DonetickError(f"API error {e.response.status_code}: {e.response.text}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _request(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Any:
        """Make an authenticated API request with retries."""
        response = self._client.request(method, path, json=json, params=params)
        self._handle_error(response)
        return response.json()
    
    def close(self) -> None:
        """Close the HTTP client connection."""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    # Tasks API
    
    def list_tasks(
        self,
        status: Optional[str] = None,
        group_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Task]:
        """List tasks with optional filtering.
        
        Args:
            status: Filter by status (pending, completed, overdue)
            group_id: Filter by group
            assignee_id: Filter by assignee
            limit: Maximum results to return (default: 50)
            offset: Pagination offset (default: 0)
        
        Returns:
            List of Task objects
        """
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if group_id:
            params["group_id"] = group_id
        if assignee_id:
            params["assignee_id"] = assignee_id
        
        data = self._request("GET", "/tasks", params=params)
        return [Task.model_validate(item) for item in data]
    
    def get_task(self, task_id: str) -> Task:
        """Get a single task by ID.
        
        Args:
            task_id: UUID of the task
        
        Returns:
            Task object
        """
        data = self._request("GET", f"/tasks/{task_id}")
        return Task.model_validate(data)
    
    def create_task(self, task: TaskCreate) -> Task:
        """Create a new task.
        
        Args:
            task: TaskCreate model with task details
        
        Returns:
            Created Task object
        """
        data = self._request("POST", "/tasks", json=task.model_dump(exclude_none=True))
        return Task.model_validate(data)
    
    def update_task(self, task_id: str, task: TaskUpdate) -> Task:
        """Update an existing task.
        
        Args:
            task_id: UUID of the task to update
            task: TaskUpdate model with fields to update
        
        Returns:
            Updated Task object
        """
        data = self._request(
            "PUT",
            f"/tasks/{task_id}",
            json=task.model_dump(exclude_none=True),
        )
        return Task.model_validate(data)
    
    def complete_task(self, task_id: str) -> dict:
        """Mark a task as completed.
        
        Args:
            task_id: UUID of the task to complete
        
        Returns:
            API response dict
        """
        return self._request("POST", f"/tasks/{task_id}/complete")
    
    def delete_task(self, task_id: str) -> None:
        """Delete a task.
        
        Args:
            task_id: UUID of the task to delete
        """
        self._request("DELETE", f"/tasks/{task_id}")
    
    # Things API
    
    def list_things(self) -> list[Thing]:
        """List all things (data tracking items).
        
        Returns:
            List of Thing objects
        """
        data = self._request("GET", "/things")
        return [Thing.model_validate(item) for item in data]
    
    def get_thing(self, thing_id: str) -> Thing:
        """Get a single thing by ID.
        
        Args:
            thing_id: UUID of the thing
        
        Returns:
            Thing object
        """
        data = self._request("GET", f"/things/{thing_id}")
        return Thing.model_validate(data)


class AsyncDonetickClient:
    """Async client for interacting with Donetick API.
    
    Args:
        base_url: URL of your Donetick instance (e.g., http://10.0.0.100:2021)
        token: JWT authentication token
        timeout: Request timeout in seconds (default: 30)
    
    Example:
        >>> async with AsyncDonetickClient("http://10.0.0.100:2021", "your-token") as client:
        ...     tasks = await client.list_tasks()
        ...     for task in tasks:
        ...         print(task.title)
    """
    
    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=f"{self.base_url}/api/v1",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            timeout=timeout,
        )
    
    def _handle_error(self, response: httpx.Response) -> None:
        """Convert HTTP errors to Donetick exceptions."""
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise DonetickAuthError("Invalid or expired token") from e
            elif e.response.status_code == 404:
                raise DonetickNotFoundError(f"Resource not found: {e.response.url}") from e
            elif e.response.status_code == 400:
                raise DonetickValidationError(f"Validation error: {e.response.text}") from e
            else:
                raise DonetickError(f"API error {e.response.status_code}: {e.response.text}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _request(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Any:
        """Make an authenticated API request with retries."""
        response = await self._client.request(method, path, json=json, params=params)
        self._handle_error(response)
        return response.json()
    
    async def close(self) -> None:
        """Close the HTTP client connection."""
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.close()
    
    # Tasks API
    
    async def list_tasks(
        self,
        status: Optional[str] = None,
        group_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Task]:
        """List tasks with optional filtering.
        
        Args:
            status: Filter by status (pending, completed, overdue)
            group_id: Filter by group
            assignee_id: Filter by assignee
            limit: Maximum results to return (default: 50)
            offset: Pagination offset (default: 0)
        
        Returns:
            List of Task objects
        """
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if group_id:
            params["group_id"] = group_id
        if assignee_id:
            params["assignee_id"] = assignee_id
        
        data = await self._request("GET", "/tasks", params=params)
        return [Task.model_validate(item) for item in data]
    
    async def get_task(self, task_id: str) -> Task:
        """Get a single task by ID.
        
        Args:
            task_id: UUID of the task
        
        Returns:
            Task object
        """
        data = await self._request("GET", f"/tasks/{task_id}")
        return Task.model_validate(data)
    
    async def create_task(self, task: TaskCreate) -> Task:
        """Create a new task.
        
        Args:
            task: TaskCreate model with task details
        
        Returns:
            Created Task object
        """
        data = await self._request("POST", "/tasks", json=task.model_dump(exclude_none=True))
        return Task.model_validate(data)
    
    async def update_task(self, task_id: str, task: TaskUpdate) -> Task:
        """Update an existing task.
        
        Args:
            task_id: UUID of the task to update
            task: TaskUpdate model with fields to update
        
        Returns:
            Updated Task object
        """
        data = await self._request(
            "PUT",
            f"/tasks/{task_id}",
            json=task.model_dump(exclude_none=True),
        )
        return Task.model_validate(data)
    
    async def complete_task(self, task_id: str) -> dict:
        """Mark a task as completed.
        
        Args:
            task_id: UUID of the task to complete
        
        Returns:
            API response dict
        """
        return await self._request("POST", f"/tasks/{task_id}/complete")
    
    async def delete_task(self, task_id: str) -> None:
        """Delete a task.
        
        Args:
            task_id: UUID of the task to delete
        """
        await self._request("DELETE", f"/tasks/{task_id}")
    
    # Things API
    
    async def list_things(self) -> list[Thing]:
        """List all things (data tracking items).
        
        Returns:
            List of Thing objects
        """
        data = await self._request("GET", "/things")
        return [Thing.model_validate(item) for item in data]
    
    async def get_thing(self, thing_id: str) -> Thing:
        """Get a single thing by ID.
        
        Args:
            thing_id: UUID of the thing
        
        Returns:
            Thing object
        """
        data = await self._request("GET", f"/things/{thing_id}")
        return Thing.model_validate(data)
