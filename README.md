# Donetick API Client

[![PyPI](https://img.shields.io/pypi/v/donetick-api-client)](https://pypi.org/project/donetick-api-client/)
[![Python](https://img.shields.io/pypi/pyversions/donetick-api-client)](https://pypi.org/project/donetick-api-client/)

A Python client library for the [Donetick](https://github.com/donetick/donetick) task and chore management API.

## Features

- 📝 **Full Task API**: Create, read, update, delete, and complete tasks
- 📊 **Things Support**: Track custom data points (counters, booleans, text)
- 🔄 **Automatic Retries**: Exponential backoff for transient failures
- 🔒 **Type Safety**: Pydantic models for all API responses
- ⚡ **Sync & Async**: Synchronous client (async coming soon)

## Installation

```bash
pip install donetick-api-client
```

## Quick Start

```python
from donetick import DonetickClient

# Connect to your self-hosted Donetick instance
client = DonetickClient(
    base_url="http://10.0.0.100:2021",
    token="your-jwt-token"
)

# List pending tasks
tasks = client.list_tasks(status="pending")
for task in tasks:
    print(f"{task.title} - Due: {task.due_date}")

# Complete a task
client.complete_task("task-uuid-here")
```

## API Coverage

| Endpoint | Status |
|----------|--------|
| `GET /tasks` | ✅ List tasks |
| `POST /tasks` | ✅ Create task |
| `GET /tasks/{id}` | ✅ Get task |
| `PUT /tasks/{id}` | ✅ Update task |
| `POST /tasks/{id}/complete` | ✅ Complete task |
| `DELETE /tasks/{id}` | ✅ Delete task |
| `GET /things` | ✅ List things |
| `GET /things/{id}` | ✅ Get thing |

## Configuration

Get your JWT token from your Donetick instance settings.

## Development

```bash
# Clone the repo
git clone https://github.com/NotoHACS/donetick-api-client.git
cd donetick-api-client

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
ruff format .

# Run type checking
mypy src/donetick
```

## License

MIT License - see [LICENSE](LICENSE) for details.

Python client for Donetick task/chore API
