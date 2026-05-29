import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
    retry_if_exception_type
)
from app.config import settings
from app.logger import logger

# Log retry attempts using structlog
class TenacityLoggerAdapter:
    def __init__(self, logger):
        self.logger = logger
    
    def log(self, level, msg, *args, **kwargs):
        # Map levels to structlog
        if level == logging.WARNING:
            self.logger.warning(msg, *args, **kwargs)
        elif level == logging.ERROR:
            self.logger.error(msg, *args, **kwargs)
        else:
            self.logger.info(msg, *args, **kwargs)

retry_logger = TenacityLoggerAdapter(logger)

def get_ollama_retry_decorator():
    """
    Returns a retry decorator customized for Ollama API communication.
    It retries on ConnectionError, TimeoutError, and other transient network issues.
    """
    return retry(
        stop=stop_after_attempt(settings.RETRY_MAX_ATTEMPTS),
        wait=wait_exponential(
            multiplier=1,
            min=settings.RETRY_MIN_WAIT_SECONDS,
            max=settings.RETRY_MAX_WAIT_SECONDS
        ),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, IOError, Exception)),
        before_sleep=before_sleep_log(retry_logger, logging.WARNING),
        reraise=True
    )
