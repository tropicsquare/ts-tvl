# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import logging
import logging.config
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence

if TYPE_CHECKING:
    _LoggerAdapter = logging.LoggerAdapter[logging.Logger]
else:
    _LoggerAdapter = logging.LoggerAdapter


class Colors(str, Enum):
    """
    Enumeration of colors
    """

    BLACK = "\x1b[90m"
    RED = "\x1b[91m"
    GREEN = "\x1b[92m"
    YELLOW = "\x1b[93m"
    BLUE = "\x1b[94m"
    PURPLE = "\x1b[95m"
    CYAN = "\x1b[96m"
    NONE = "\x1b[0m"

    __str__ = str.__str__


class TVLFormatter(logging.Formatter):
    """
    Logging formatter that can issue colored log messages
    """

    LOG_FORMAT = "[%(levelname)s] [%(name)s] %(message)s"
    COLORS = {
        logging.DEBUG: Colors.BLUE,
        logging.INFO: Colors.PURPLE,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.RED,
    }

    def __init__(self, use_colors: bool = True, **kwargs: Any):
        log_format = kwargs.get("format", self.LOG_FORMAT)
        if use_colors:
            log_format = f"%(color)s{log_format}{Colors.NONE}"
            self.format = self._format_with_colors
        super().__init__(fmt=log_format)

    def _format_with_colors(self, record: logging.LogRecord) -> str:
        record.color = self.COLORS.get(record.levelno, Colors.NONE)
        return super().format(record)


class Labeller(_LoggerAdapter):
    def __init__(self, logger: logging.Logger, label: str) -> None:
        """LoggerAdapter adding an extra field `label` to the log records"""
        super().__init__(logger, {"label": label})


class LabelFilter(logging.Filter):
    def __init__(self, labels: Sequence[str]) -> None:
        """Filter removing out the log records with some label

        Args:
            labels (Sequence[str]): the labels to be filtered
        """
        self.labels = labels

    def filter(self, record: logging.LogRecord) -> bool:
        label: Optional[str] = getattr(record, "label", None)
        return label is None or label not in self.labels


def setup_logging(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Setup logging inside TVL
    """
    if config is None:
        config = {
            "version": 1,
            "formatters": {
                "default": {
                    "()": f"{TVLFormatter.__module__}.{TVLFormatter.__name__}",
                    "format": "[%(name)s] [%(levelname)s] %(message)s",
                    "use_colors": True,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "loggers": {},
            "root": {
                "level": "DEBUG",
                "handlers": ["console"],
            },
        }
    return logging.config.dictConfig(config)
