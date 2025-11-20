from tools.logger import Logger, LogType


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
