#!/usr/bin/env python3

# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import logging
from argparse import ArgumentParser, ArgumentTypeError, RawTextHelpFormatter
from pathlib import Path
from typing import Callable, Iterable

from tvl.api_generator.internal import (
    LANGUAGES,
    TEMPLATE_DIR,
    __version__,
    generate_api_files,
    get_suffix,
)


def get_input_arguments():
    def _with_ext(ext: Iterable[str]) -> Callable[[Path], Path]:
        def _check(p: Path) -> Path:
            if get_suffix(p) not in ext:
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
        description="Generate API files from a yaml API description file.",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"API Generator version {__version__}",
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
        type=_input_file(_with_ext([".yaml", ".yml"])),
        help="Input yaml API description file",
        metavar="FILE",
    )
    _output_args_help = [
        "Name of the API files:",
        *(f"'*{info.extension}': generate {info.name} API file" for info in LANGUAGES),
    ]
    parser.add_argument(
        "-o",
        "--output-files",
        nargs="+",
        required=True,
        type=_output_file(_with_ext([info.extension for info in LANGUAGES])),
        help="\n".join(_output_args_help),
        metavar="FILE",
    )
    _templates_args_help = ["Name of the custom template files:"]
    for info in LANGUAGES:
        _templates_args_help.append(
            f" - '*{info.template_extension}': override "
            f"default {info.name} template: '{info.default_template.name}'"
        )
    _templates_args_help.append("List of available default templates:")
    for info in LANGUAGES:
        _templates_args_help.extend(
            sorted(
                f" - {p.name}" for p in TEMPLATE_DIR.glob(f"*{info.template_extension}")
            )
        )
    parser.add_argument(
        "-t",
        "--templates",
        nargs="+",
        type=_template(_with_ext([info.template_extension for info in LANGUAGES])),
        help="\n".join(_templates_args_help),
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
    generate_api_files(**vars(args))


if __name__ == "__main__":
    main()
