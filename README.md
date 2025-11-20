# Python uv Template - Minimal (POC Version)

A lightweight Python development template using **uv** (fast package manager) and **Ruff** (linter/formatter). Perfect for quick POCs and prototypes.

## Quick Start (5 minutes)

### Prerequisites

- Python 3.10+ 
- [uv](https://docs.astral.sh/uv/) installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Setup

```bash
# Clone and navigate
git clone <your-repo-url>
cd python-uv

# Install dependencies
uv sync

# Run tests
uv run pytest

# Format and lint
uv run ruff format .
uv run ruff check . --fix
```

## What's Included

### Core Utilities (`tools/`)

- **Logger**: Dual-mode logging (colored console for local, structured JSON for production)
- **Config**: Environment-based configuration using Pydantic
- **Timer**: Performance monitoring decorator/context manager

### Usage Examples

```python
# Logger
from tools import Logger, LogType, Settings

settings = Settings()
logger = Logger(
    __name__,
    log_type=LogType.LOCAL if settings.IS_LOCAL else LogType.AZURE_MONITOR
)
logger.info("Hello world")

# Config
from tools import Settings

settings = Settings()
print(settings.DEBUG)

# Timer
from tools import Timer

@Timer("operation")
def my_function():
    # Your code here
    pass
```

## Configuration

Create `.env.local` for local overrides (ignored by git):

```bash
# Environment
IS_LOCAL=true
DEBUG=true

# Azure Monitor (Production only)
APPLICATIONINSIGHTS_CONNECTION_STRING=your-connection-string
```

## Optional Dependencies

```bash
# FastAPI support
uv sync --extra fastapi

# Database support (SQLAlchemy + Alembic)
uv sync --extra database

# Everything
uv sync --extra all
```

## Development Commands

```bash
# Add dependency
uv add <package>

# Add dev dependency
uv add --dev <package>

# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint code
uv run ruff check . --fix
uv run pyright

# Type check
uv run pyright
```

## Project Structure

```
.
├── tools/              # Reusable utilities
│   ├── config/        # Settings & environment
│   ├── logger/        # Logging system
│   └── tracer/        # Performance monitoring
├── tests/             # Unit tests
├── .env               # Environment template (committed)
├── .env.local         # Local overrides (gitignored)
└── pyproject.toml     # Dependencies & metadata
```

## License

MIT License - See [LICENSE](LICENSE) for details.
