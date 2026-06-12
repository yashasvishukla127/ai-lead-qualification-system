# src/utils/logger.py
import logging
import uuid
from contextvars import ContextVar

# One ContextVar per async task — safe with FastAPI's async handlers
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    return correlation_id_var.get() or str(uuid.uuid4())


def set_correlation_id(value: str) -> object:
    """Returns the reset token — call correlation_id_var.reset(token) when done."""
    return correlation_id_var.set(value)


class CorrelationFilter(logging.Filter):
    """Injects correlation_id into every LogRecord automatically."""
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id()
        return True


def configure_logging() -> None:
    fmt = "%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(name)s | %(message)s"
    handler = logging.StreamHandler()
    handler.addFilter(CorrelationFilter())
    handler.setFormatter(logging.Formatter(fmt))

    logging.basicConfig(level=logging.INFO, handlers=[handler])
    # Also attach the filter to the file handler for errors.log
    file_handler = logging.FileHandler("errors.log")
    file_handler.setLevel(logging.ERROR)
    file_handler.addFilter(CorrelationFilter())
    file_handler.setFormatter(logging.Formatter(fmt))
    logging.getLogger().addHandler(file_handler)