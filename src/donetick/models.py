"""Pydantic models for Donetick API."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class Subtask(BaseModel):
    """A subtask within a task."""
    model_config = ConfigDict(populate_by_name=True)
    
    title: str
    completed: bool = False


class Task(BaseModel):
    """Represents a Donetick task.
    
    Attributes:
        id: UUID of the task
        title: Task title
        description: Optional task description
        due_date: When the task is due (ISO 8601)
        status: Current status (pending, completed, overdue)
        priority: Priority level (P1-P4, or None)
        labels: List of label strings
        subtasks: Nested subtasks
        group_id: UUID of the owning group
        assignee_id: UUID of the assigned user
        created_at: When the task was created
        updated_at: When the task was last updated
    """
    model_config = ConfigDict(populate_by_name=True)
    
    id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = "pending"  # pending, completed, overdue
    priority: Optional[str] = None  # P1, P2, P3, P4, or None
    labels: list[str] = Field(default_factory=list)
    subtasks: list[Subtask] = Field(default_factory=list)
    group_id: Optional[str] = None
    assignee_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TaskCreate(BaseModel):
    """Model for creating a new task.
    
    Attributes:
        title: Required task title
        description: Optional description
        due_date: Optional due date
        recurrence: Recurrence pattern (daily, weekly, monthly, yearly)
        priority: Priority level (P1-P4)
        labels: Optional list of labels
        subtasks: Optional list of subtasks
        group_id: Optional group to assign to
        assignee_id: Optional user to assign to
    """
    model_config = ConfigDict(populate_by_name=True)
    
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = None  # daily, weekly, monthly, yearly
    priority: Optional[str] = None  # P1, P2, P3, P4
    labels: Optional[list[str]] = None
    subtasks: Optional[list[Subtask]] = None
    group_id: Optional[str] = None
    assignee_id: Optional[str] = None


class TaskUpdate(BaseModel):
    """Model for updating an existing task.
    
    All fields are optional - only provided fields will be updated.
    """
    model_config = ConfigDict(populate_by_name=True)
    
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = None
    priority: Optional[str] = None
    labels: Optional[list[str]] = None
    subtasks: Optional[list[Subtask]] = None
    group_id: Optional[str] = None
    assignee_id: Optional[str] = None


class Thing(BaseModel):
    """Represents a Donetick Thing (data tracking item).
    
    Things track non-task data like counters, booleans, or text values.
    
    Attributes:
        id: UUID of the thing
        name: Thing name
        type: Data type (number, boolean, text)
        value: Current value (type varies by thing type)
        group_id: UUID of the owning group
        created_at: When the thing was created
    """
    model_config = ConfigDict(populate_by_name=True)
    
    id: str
    name: str
    type: str  # number, boolean, text
    value: Any
    group_id: Optional[str] = None
    created_at: Optional[datetime] = None


class Group(BaseModel):
    """Represents a Donetick group.
    
    Groups are shared spaces for tasks and things.
    
    Attributes:
        id: UUID of the group
        name: Group name
        description: Optional description
        created_at: When the group was created
    """
    model_config = ConfigDict(populate_by_name=True)
    
    id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None


class User(BaseModel):
    """Represents a Donetick user.
    
    Attributes:
        id: UUID of the user
        username: Username
        email: Email address
        points: Current point total
    """
    model_config = ConfigDict(populate_by_name=True)
    
    id: str
    username: str
    email: Optional[str] = None
    points: int = 0
