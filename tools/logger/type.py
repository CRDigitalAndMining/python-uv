from enum import StrEnum, auto


class LogType(StrEnum):
    """Logger type.

    Attributes:
        LOCAL: Colored console output for local development
        AZURE_MONITOR: Structured JSON logging for Azure Monitor/Application Insights
        AWS: Reserved for future AWS CloudWatch integration (not yet implemented)

    """

    LOCAL = auto()
    AZURE_MONITOR = auto()
    AWS = auto()  # Reserved for future use
