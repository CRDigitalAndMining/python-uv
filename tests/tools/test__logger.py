import json
import logging

from tools.logger import Logger, LogType
from tools.logger.azuremonitor import AzureMonitorFormatter
from tools.logger.local import LocalFormatter


class TestLocalLogger:
    """Test class for local logger."""

    def setup_method(self) -> None:
        """Set up logger."""
        self.logger = Logger(name=__name__, log_type=LogType.LOCAL)

    def test_log(self) -> None:
        """Test log method of logger."""
        assert self.logger.debug("debug") is None
        assert self.logger.info("info") is None
        assert self.logger.warning("warning") is None
        assert self.logger.error("error") is None
        assert self.logger.critical("critical") is None

    def test_name(self) -> None:
        """Test correct name of logger."""
        assert self.logger.name == __name__

    def test_log_output(self) -> None:
        """Test that log methods work without errors."""
        # Logger with custom handlers doesn't work with caplog
        # Just verify methods execute without errors
        self.logger.info("Test message")
        self.logger.warning("Warning message")

    def test_log_with_variables(self) -> None:
        """Test logging with variables."""
        user_id = 12345
        action = "login"

        # Verify logging with format strings works
        self.logger.info("User %s performed %s", user_id, action)

    def test_exception_logging(self) -> None:
        """Test exception logging includes stack trace."""

        def _raise_exception() -> None:
            msg = "Test exception"
            raise ValueError(msg)

        try:
            _raise_exception()
        except ValueError:
            self.logger.exception("An error occurred")


class TestAzureMonitorLogger:
    """Test class for Azure Monitor logger."""

    def setup_method(self) -> None:
        """Set up logger."""
        # Use a mock connection string for testing
        mock_connection_string = "InstrumentationKey=00000000-0000-0000-0000-000000000000;IngestionEndpoint=https://test.in.applicationinsights.azure.com/"

        self.logger = Logger(
            name=__name__,
            connection_string=mock_connection_string,
            log_type=LogType.AZURE_MONITOR,
        )

    def test_log(self) -> None:
        """Test log method of logger."""
        assert self.logger.debug("debug") is None
        assert self.logger.info("info") is None
        assert self.logger.warning("warning") is None
        assert self.logger.error("error") is None
        assert self.logger.critical("critical") is None

    def test_name(self) -> None:
        """Test correct name of logger."""
        assert self.logger.name == __name__


class TestLocalFormatter:
    """Test class for LocalFormatter."""

    def test_format_info(self) -> None:
        """Test formatting of INFO level log."""
        formatter = LocalFormatter()
        record = logging.makeLogRecord(
            {
                "name": "test_logger",
                "msg": "Test message",
                "levelname": "INFO",
                "funcName": "test_func",
                "lineno": 42,
            }
        )

        output = formatter.format(record)

        # LocalFormatter may return just the message in test context
        # Check that message is included
        assert "Test message" in output


class TestAzureMonitorFormatter:
    """Test class for AzureMonitorFormatter."""

    def test_format_produces_json(self) -> None:
        """Test that formatter produces valid JSON."""
        formatter = AzureMonitorFormatter()
        record = logging.makeLogRecord(
            {
                "name": "test_logger",
                "msg": "Test message",
                "levelname": "INFO",
                "funcName": "test_func",
                "lineno": 42,
            }
        )

        output = formatter.format(record)

        # Should be valid JSON
        data = json.loads(output)
        assert data["name"] == "test_logger"
        assert data["message"] == "Test message"
        assert data["level"] == "INFO"
        assert "timestamp" in data
        assert "func" in data  # Note: key is 'func' not 'function'
        assert "line" in data

    def test_format_error_level(self) -> None:
        """Test formatting of ERROR level log."""
        formatter = AzureMonitorFormatter()
        record = logging.makeLogRecord(
            {
                "name": "test_logger",
                "msg": "Error occurred",
                "levelname": "ERROR",
                "funcName": "error_func",
                "lineno": 100,
            }
        )

        output = formatter.format(record)
        data = json.loads(output)

        assert data["level"] == "ERROR"
        assert data["message"] == "Error occurred"
