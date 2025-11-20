# GitHub Copilot Instructions - Minimal POC Branch

This is a **minimal branch** for quick POCs and prototypes. Keep it simple!

## Project Overview

Lightweight Python template using **uv** (package manager) and **Ruff** (linter/formatter).

Core utilities in `tools/`:
- **Logger**: Dual-mode logging (local/Azure Monitor)
- **Config**: Environment-based settings (Pydantic)
- **Timer**: Performance monitoring decorator/context manager

## Development Commands

### Package Management
```bash
# Install dependencies
uv sync

# Add new dependency
uv add <package>

# Add dev dependency
uv add --dev <package>

# Remove dependency
uv remove <package>
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test__minimal.py

# Run with verbose output
uv run pytest -v
```

### Linting & Formatting
```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check . --fix

# Type check
uv run pyright
```

## Architecture

### Core Modules

The `tools/` package provides three main utility modules:

#### **tools/logger/** - Dual-Mode Logging System
- `Logger` class extends `logging.Logger` with environment-aware formatting
- **LogType.LOCAL**: Colored console output via `LocalFormatter` for development
- **LogType.AZURE_MONITOR**: Structured JSON via `AzureMonitorFormatter` for production on Azure
- Key pattern: Use `Settings.IS_LOCAL` to switch between modes automatically

```python
from tools.config import Settings
from tools.logger import Logger, LogType

settings = Settings()
logger = Logger(
    __name__,
    log_type=LogType.LOCAL if settings.IS_LOCAL else LogType.AZURE_MONITOR
)
```

#### **tools/config/** - Environment-Based Configuration
- `Settings` class uses Pydantic for type-safe configuration
- Loads from `.env` (version controlled) and `.env.local` (local overrides, in .gitignore)
- `FastAPIKwArgs` provides ready-to-use FastAPI initialization parameters
- Pattern: Extend `Settings` to add project-specific configuration fields

```python
from tools.config import Settings

settings = Settings()
api_url = settings.api_prefix_v1  # Loaded from environment
```

#### **tools/tracer/** - Performance Monitoring
- `Timer` class works as both decorator and context manager
- Automatically logs execution time in milliseconds at DEBUG level
- Uses the `Logger` module for output (inherits logging configuration)
- Pattern: Nest timers to measure both overall and component performance

```python
from tools.tracer import Timer

@Timer("full_operation")
def process():
    with Timer("step1"):
        do_step1()
    with Timer("step2"):
        do_step2()
```

### Test Structure

Tests in `tests/`:
- **Naming convention**: `test__*.py` (double underscore)
- **Coverage**: Not enforced in minimal branch (for speed)
- **Minimal smoke tests**: Only essential functionality tests

### Configuration Philosophy

**Ruff (ruff.toml)**:
- Essential rules only: E (errors), F (pyflakes), I (isort), UP (pyupgrade)
- Line length: 88 (Black-compatible)
- Target Python: 3.14
- Per-file ignores for test files

**Pyright (pyrightconfig.json)**:
- Type checking mode: standard
- Only includes `tools/` package (not tests)
- venv: `/home/vscode/.venv`

**pytest (pytest.ini)**:
- Basic test discovery
- Simple output format
- No coverage requirements

## Key Patterns for Development

### Adding New Configuration Fields

Extend the `Settings` class in `tools/config/settings.py`:

```python
class Settings(BaseSettings):
    # Existing fields...

    # Add your new fields
    NEW_SETTING: str = "default_value"
    ANOTHER_SETTING: int = 42
```

Then add to `.env.local`:
```bash
NEW_SETTING=custom_value
ANOTHER_SETTING=100
```

### Adding New Logger Formatters

Create a new formatter in `tools/logger/`:
1. Extend `logging.Formatter`
2. Export from `tools/logger/__init__.py`
3. Update `Logger.__init__()` to support the new type

### Testing Utilities

When testing the utilities themselves:
- Logger: Capture logs using `assertLogs` context manager
- Config: Use Pydantic's model instantiation with kwargs to override values
- Timer: Check debug logs for execution time messages

## Environment Variables

Critical environment variables (set in `.env.local`):
- `IS_LOCAL`: Boolean flag for local vs production (affects logging, configuration)
- `debug`: Boolean for debug mode
- FastAPI settings: `title`, `version`, `api_prefix_v1`, etc.

## Important Notes

- **Minimal configuration**: Only essential rules and tools
- **uv replaces pip/poetry**: Use `uv add` not `pip install`, use `uv.lock` not `requirements.txt`
- **Ruff replaces multiple tools**: No need for Black, isort, Flake8, etc.
- **No task runner**: Run commands directly with `uv run`
- **Test naming**: Use `test__*.py` pattern (double underscore)
- **Type checking targets tools/ only**: Pyright only checks the `tools/` package, not tests

## Template Usage Pattern

When using this as a template for a new POC:
1. Clone the minimal branch
2. Update `pyproject.toml` with new project name/description
3. Modify or extend `tools/config/settings.py` for project-specific configuration
4. Use the utilities from `tools/` or remove if not needed
5. Update `.env` with base configuration, `.env.local` with local overrides

## Optional Dependencies

```bash
# FastAPI support
uv sync --extra fastapi

# Database support (SQLAlchemy + Alembic)
uv sync --extra database

# Everything
uv sync --extra all
```

## Development Philosophy

This minimal branch is optimized for:
- ✅ Fast iteration
- ✅ Quick prototyping  
- ✅ Minimal overhead
- ✅ Essential tooling only

**Not included** (use main branch for production):
- ❌ Extensive documentation
- ❌ CI/CD pipelines
- ❌ Pre-commit hooks
- ❌ Coverage requirements
- ❌ Task automation (nox)
