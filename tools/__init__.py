"""Tools - Production-ready utilities for Python applications.

This package provides reusable utilities for building modern Python applications:
- Logger: Dual-mode logging (local console / Azure Monitor)
- Config: Environment-based settings management
- Tracer: Performance monitoring with Timer

Examples:
    >>> from tools import Logger, LogType, Settings, Timer
    >>>
    >>> settings = Settings()
    >>> log_type = LogType.LOCAL if settings.IS_LOCAL else LogType.AZURE_MONITOR
    >>> logger = Logger(__name__, log_type=log_type)
    >>>
    >>> @Timer("my_function")
    >>> def my_function():
    >>>     logger.info("Function executed")

"""

from tools.config import FastAPIKwArgs, Settings
from tools.logger import Logger, LogType
from tools.tracer import Timer

__all__ = [
    "FastAPIKwArgs",
    "LogType",
    "Logger",
    "Settings",
    "Timer",
]
