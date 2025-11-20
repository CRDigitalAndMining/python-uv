import logging
import sys
from typing import TYPE_CHECKING

from tools.logger.type import LogType

if TYPE_CHECKING:
    from azure.identity import DefaultAzureCredential


class Logger(logging.Logger):
    """Logger.

    Examples:
        >>> from tools.logger import Logger
        >>>
        >>>
        >>> logger = Logger(__name__)
        >>> logger.info("Logger")

    """

    def __init__(
        self,
        name: str,
        connection_string: str | None = None,
        credential: DefaultAzureCredential | None = None,
        log_type: LogType = LogType.LOCAL,
    ) -> None:
        """Initialize local logger formatter.

        Args:
            name (str): Logger name
            connection_string (str | None, optional): Azure Monitor connection string.
                                                      Defaults to None.
            credential (DefaultAzureCredential | None, optional): Credentials for Azure.
                                                                  Defaults to None.
            log_type (LogType, optional): Local or Azure Monitor.
                                          Defaults to LogType.LOCAL.

        """
        super().__init__(name=name)

        if log_type == LogType.AZURE_MONITOR:
            if not connection_string and not credential:
                msg = (
                    "Azure Monitor logging requires either "
                    "connection_string or credential"
                )
                raise ValueError(msg)

            from azure.monitor.opentelemetry import configure_azure_monitor

            from tools.logger import AzureMonitorFormatter

            # Configure Azure Monitor with OpenTelemetry
            configure_azure_monitor(
                connection_string=connection_string,
                credential=credential,
            )

            formatter = AzureMonitorFormatter()
            handler = logging.StreamHandler(stream=sys.stdout)

            handler.setFormatter(formatter)
            self.addHandler(handler)
            return

        from tools.logger import LocalFormatter

        formatter = LocalFormatter()
        handler = logging.StreamHandler(stream=sys.stdout)

        handler.setFormatter(formatter)
        self.addHandler(handler)
