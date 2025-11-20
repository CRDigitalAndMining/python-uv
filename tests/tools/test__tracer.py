import time

from tools.tracer import Timer


class TestTimer:
    """Test class for Timer."""

    def test_contextmanager(self) -> None:
        """Test for ContextManager."""
        with Timer("ContextManager"):
            pass

    @Timer("Decorator")
    def test_decorator(self) -> None:
        """Test for Decorator."""

    def test_timer_measures_duration(self) -> None:
        """Test that Timer measures execution time."""
        # Timer logs with custom handler, can't capture with caplog
        # Just verify it executes without error
        with Timer("test_duration"):
            time.sleep(0.1)  # Sleep for 100ms

    def test_timer_as_decorator_logs(self) -> None:
        """Test that Timer as decorator logs execution time."""

        @Timer("decorated_function")
        def sample_function() -> str:
            time.sleep(0.05)
            return "done"

        result = sample_function()
        assert result == "done"

    def test_timer_duration_property(self) -> None:
        """Test that Timer duration property works correctly."""
        timer = Timer("test")
        timer.__enter__()
        time.sleep(0.1)
        timer.__exit__()

        # Duration should be approximately 0.1 seconds (allow some variance)
        min_duration = 0.08
        max_duration = 0.15
        assert min_duration <= timer._duration <= max_duration  # noqa: SLF001

    def test_nested_timers(self) -> None:
        """Test nested timers work correctly."""
        # Timer logs with custom handler, just verify execution
        with Timer("outer"):
            time.sleep(0.05)
            with Timer("inner"):
                time.sleep(0.05)
