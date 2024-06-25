import logging
from pprint import pformat
from shutil import get_terminal_size
from typing import Any, Dict, Iterable


class LogDict:
    def __init__(self, dct: Dict[Any, Any]) -> None:
        self.dct = dct

    def __str__(self) -> str:
        return "\n" + pformat(self.dct, width=get_terminal_size()[0])


class LogIter:
    def __init__(self, iter: Iterable[Any], fmt: str, sep: str = ",") -> None:
        self.iterable = iter
        self.fmt = fmt
        self.sep = sep

    def __str__(self) -> str:
        return self.sep.join(self.fmt % elt for elt in self.iterable)


def configure_logging(verbose: int) -> None:
    try:
        level = [logging.WARNING, logging.INFO][verbose]
    except IndexError:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="[%(levelname)s] [%(name)s] %(message)s")
