import logging

from src.commonlib.config import settings


def setup_logger(name: str, level: int = settings.LOGGING_LEVEL) -> logging.Logger:
    """
    Set up a logger

    Args:
        name (str): service name
        level (int): Logging level

    Returns:
        logging.Logger: Configured logger instance
    """
    # create logger
    logger = logging.getLogger(name=name)
    logger.setLevel(level=level)

    # create console handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s %(name)s [%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Set level and attach formatter and handler
    logger.addHandler(handler)
    handler.setLevel(level=level)
    handler.setFormatter(formatter)

    return logger


search_logger: logging.Logger = setup_logger("search-agent")
