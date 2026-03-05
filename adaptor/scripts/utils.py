import json
import logging
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel


# Logger
class InfoFilter(logging.Filter):
    """
    Info messages filter for logging handlers.
    """

    def filter(self, record) -> bool:
        return record.levelno == logging.INFO


class NonInfoFilter(logging.Filter):
    """
    Non Info messages filter for logging handlers.
    """

    def filter(self, record) -> bool:
        return record.levelno != logging.INFO


class LoggingConfig:
    """Logging handler setups."""

    @staticmethod
    def _stream_handler_config() -> None:
        """Initialize StreanHandler"""
        stream_handler = logging.StreamHandler()
        stream_formatter = logging.Formatter(
            "%(levelname)s %(pathname)s:%(funcName)s:%(lineno)d -> %(asctime)s %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        stream_handler.setFormatter(stream_formatter)
        stream_handler.addFilter(NonInfoFilter())
        logger.addHandler(stream_handler)

    @staticmethod
    def _file_handler_config() -> None:
        """Initialize FileHandler"""
        try:
            logs_folder = Path(__file__).parents[1] / "logs"
            if not logs_folder.exists():
                os.makedirs(logs_folder)

            file_handler = logging.FileHandler(logs_folder / "info.log")
            file_formatter = logging.Formatter(
                "%(asctime)s %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            file_handler.addFilter(InfoFilter())
            logger.addHandler(file_handler)
        except FileNotFoundError:
            raise


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

LoggingConfig._stream_handler_config()
# LoggingConfig._file_handler_config()


# Config values
class ConfigValidation(BaseModel):
    """config.json file values."""

    model: str


def _read_json_file() -> Any | None:
    config_path = Path(__file__).parents[1] / "data/config.json"
    try:
        with config_path.open(encoding="utf-8") as file:
            config_values = json.load(file)
            return config_values
    except FileNotFoundError:
        logger.error("Config file not found.")


try:
    config_args = ConfigValidation.model_validate(_read_json_file())
except ValueError:
    logger.error("Validation failed.")
