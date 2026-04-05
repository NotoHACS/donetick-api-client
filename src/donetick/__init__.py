"""Donetick API Client - Python client for self-hosted Donetick."""

from .client import AsyncDonetickClient, DonetickClient
from .exceptions import (
    DonetickError,
    DonetickAuthError,
    DonetickNotFoundError,
    DonetickValidationError,
)
from .models import Task, Thing, Group, User

__version__ = "0.1.0"

__all__ = [
    "AsyncDonetickClient",
    "DonetickClient",
    "DonetickError",
    "DonetickAuthError",
    "DonetickNotFoundError",
    "DonetickValidationError",
    "Task",
    "Thing",
    "Group",
    "User",
]
