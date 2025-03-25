import logging
import logging.config
import sys
from pathlib import Path
from pprint import pformat
from shutil import get_terminal_size
from typing import Any, Callable, Dict, Iterable, Optional

import yaml

DEFAULT_LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "formatters": {
        "default": {
            "()": "tvl.logging_utils.TVLFormatter",
            "format": "[%(name)s] [%(levelname)s] %(message)s",
            "use_colors": True,
        },
    },
    "filters": {
        "labelfilter": {
            "()": "tvl.logging_utils.LabelFilter",
            "labels": ["spi", "uap"],
        }
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "model": {
            "level": "INFO",
            "handlers": ["default"],
            "filters": ["labelfilter"],
        },
        "server": {
            "level": "INFO",
            "handlers": ["default"],
        },
    },
}


class LogDict:
    def __init__(
        self,
        dct: Dict[Any, Any],
        *,
        fn: Optional[Callable[[Dict[Any, Any]], Any]] = None,
    ) -> None:
        self.dct = dct
        self.fn = fn

    def __str__(self) -> str:
        return "\n" + pformat(
            self.fn(self.dct) if self.fn is not None else self.dct,
            width=get_terminal_size()[0],
        )


class LogIter:
    def __init__(self, it: Iterable[Any], fmt: str, sep: str = ",") -> None:
        self.it = it
        self.fmt = fmt
        self.sep = sep

    def __str__(self) -> str:
        return self.sep.join(self.fmt % elt for elt in self.it)


def configure_logging(filepath: Optional[Path] = None) -> None:
    if filepath is None:
        config = DEFAULT_LOGGING_CONFIG
    else:
        config = yaml.safe_load(filepath.read_bytes())
    logging.config.dictConfig(config)


def dump_logging_configuration(**_: Any) -> None:
    yaml.dump(DEFAULT_LOGGING_CONFIG, stream=sys.stdout, sort_keys=False)
