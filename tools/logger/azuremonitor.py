import logging


class AzureMonitorFormatter(logging.Formatter):
    """Formatter for Azure Monitor logger."""

    def format(self, record: logging.LogRecord) -> str:
        """Style for Azure Monitor logger.

        Args:
            record (logging.LogRecord): Raw log

        Returns:
            str: Log format for Azure Monitor

        """
        from pydantic import BaseModel, PositiveInt

        class Record(BaseModel):
            """Record for Azure Monitor."""

            name: str
            line: PositiveInt
            func: str
            message: str
            level: str
            timestamp: str

        import datetime

        return Record(
            name=record.name,
            line=record.lineno,
            func=record.funcName,
            message=record.getMessage(),
            level=record.levelname,
            timestamp=datetime.datetime.fromtimestamp(
                record.created, tz=datetime.UTC
            ).isoformat(),
        ).model_dump_json()
