import logging
import sys
import uuid


class CorrelationFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = getattr(record, "correlation_id", None)
        return True


def set_correlation_id(record):
    # If correlation_id is not provided or is None, generate a new UUID
    record.correlation_id = record.correlation_id or str(uuid.uuid4())


class CustomStreamHandler(logging.StreamHandler):
    def handle(self, record):
        set_correlation_id(record)
        return super().handle(record)


def llmops_logger(
    level: int = logging.INFO, correlation_id: str = None
) -> logging.Logger:
    """Get LLMOps logger.

    Args:
        level (int, optional): Log level. Defaults to logging.INFO.
        correlation_id (str, optional): Correlation ID. Defaults to a new UUID if not provided.

    Returns:
        logging.Logger: Named logger.
    """
    logger = logging.getLogger("llmops")

    if logger.hasHandlers():
        return logger

    handler = CustomStreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s - %(correlation_id)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addFilter(CorrelationFilter())

    # If correlation_id is not provided or is None, generate a new UUID
    correlation_id = correlation_id or str(uuid.uuid4())

    # Add correlation_id as an attribute to the logger
    logger.correlation_id = correlation_id

    return logger
