from enum import StrEnum, auto


class LogType(StrEnum):
    """Logger type."""

    LOCAL = auto()
    AZURE_MONITOR = auto()
    AWS = auto()
