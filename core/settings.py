import logging
from logging.config import dictConfig

from pydantic import BaseSettings, BaseModel, validator
from typing import Optional, Union, List


class Settings(BaseSettings):

    API_V1_STR: str = "/api/v1"

    DB_PROVIDER: str = "sqlite"
    SQLALCHEMY_DATABASE_URI: Optional[str] = "sqlite:///example.db"

    class Config:
        case_sensitive = True


settings = Settings()


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "mystery_log"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        "mystery_log": {"handlers": ["default"], "level": LOG_LEVEL},
    }


dictConfig(LogConfig().dict())

logger = logging.getLogger("mystery_log")


