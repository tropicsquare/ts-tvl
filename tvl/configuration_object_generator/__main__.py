# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import logging
from argparse import ArgumentParser, ArgumentTypeError, RawTextHelpFormatter
from pathlib import Path
from typing import Callable, Iterable

from .configuration_object_generator import (
    TEMPLATE_DIR,
    __version__,
    generate_configuration_object,
)


def get_input_arguments():
    def _get_suffix(filename: Path) -> str:
        return "".join(filename.suffixes)

    def _with_ext(ext: Iterable[str]) -> Callable[[Path], Path]:
        def _check(p: Path) -> Path:
            if _get_suffix(p) not in ext:
                raise ArgumentTypeError(f"{p}: extension not in {ext}.")
            return p

        return _check

    def _input_file(fn: Callable[[Path], Path]) -> Callable[[str], Path]:
        def _check(s: str) -> Path:
            if not (p := Path(s)).exists():
                raise ArgumentTypeError(f"{p} not found.")
            if not p.is_file():
                raise ArgumentTypeError(f"{p} is not a file.")
            return fn(p)

        return _check

    def _output_file(fn: Callable[[Path], Path]) -> Callable[[str], Path]:
        def _check(s: str) -> Path:
            if (p := Path(s)).exists() and not p.is_file():
                raise ArgumentTypeError(f"{p} is not a file.")
            return fn(p)

        return _check

    def _template(fn: Callable[[Path], Path]) -> Callable[[str], Path]:
        def _check(s: str) -> Path:
            for root in (Path.cwd(), TEMPLATE_DIR):
                if (p := root.joinpath(s).resolve()).is_file():
                    return fn(p)
            raise ArgumentTypeError(f"{s} cannot be found.")

        return _check

    parser = ArgumentParser(
        description="Generate Configuration Object file from an xml description file.",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"Configuration Object Generator version {__version__}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase script verbosity",
    )
    parser.add_argument(
        "-i",
        "--input-file",
        required=True,
        type=_input_file(_with_ext([".xml"])),
        help="XML input file",
        metavar="FILE",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        required=True,
        type=_output_file(_with_ext([".py"])),
        help="Python output file",
        metavar="FILE",
    )
    parser.add_argument(
        "-t",
        "--template",
        type=_template(_with_ext([".py.j2"])),
        default=TEMPLATE_DIR.joinpath("configuration_object_impl.py.j2"),
        help="Template file; defaults to %(default)s",
        metavar="FILE",
    )
    return parser.parse_args()


def configure_logging(verbose: int) -> None:
    try:
        level = [
            logging.WARNING,
            logging.INFO,
        ][verbose]
    except IndexError:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def main() -> None:
    args = get_input_arguments()
    configure_logging(args.verbose)
    generate_configuration_object(**vars(args))


main()
