import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging(level=logging.INFO):
    """Configure structured logging for the application."""
    
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler with JSON format
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s %(module)s %(funcName)s',
        datefmt='%Y-%m-%dT%H:%M:%S%z'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Global logger instance
logger = setup_logging()