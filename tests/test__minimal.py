"""Minimal smoke tests for tools package."""

from tools.config import Settings
from tools.logger import Logger, LogType
from tools.tracer import Timer


def test_settings_loads() -> None:
    """Test that Settings can be instantiated."""
    settings = Settings()
    assert isinstance(settings.IS_LOCAL, bool)
    assert isinstance(settings.debug, bool)


def test_local_logger_creates() -> None:
    """Test that local Logger can be created."""
    logger = Logger(name="test", log_type=LogType.LOCAL)
    assert logger is not None
    logger.info("Test message")


def test_timer_measures_duration() -> None:
    """Test that Timer can measure execution time."""
    import time

    with Timer("test_operation"):
        time.sleep(0.01)  # Sleep for 10ms

    # If it doesn't raise an exception, it works


def test_timer_as_decorator() -> None:
    """Test that Timer works as a decorator."""

    @Timer("decorated_function")
    def my_function() -> str:
        return "done"

    result = my_function()
    assert result == "done"
