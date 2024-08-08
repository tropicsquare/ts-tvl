#!/usr/bin/env python3

# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import logging
from argparse import ArgumentParser, ArgumentTypeError
from functools import reduce
from pathlib import Path
from typing import Callable

from tvl.server.internal import run_server
from tvl.server.logging_utils import LogDict, configure_logging
from tvl.server.serial_connection import (
    SERIAL_DEFAULT_BAUDRATE,
    SERIAL_DEFAULT_PORT,
    generate_serial_connection,
)
from tvl.server.tcp_connection import (
    TCP_DEFAULT_ADDRESS,
    TCP_DEFAULT_PORT,
    generate_tcp_connection,
)


def get_input_arguments():
    def _with_ext(*ext: str) -> Callable[[Path], Path]:
        def _check(p: Path) -> Path:
            if p.suffix not in ext:
                raise ArgumentTypeError(f"{p}: extension not in {ext}.")
            return p

        return _check

    def _is_file(p: Path) -> Path:
        if not p.is_file():
            raise ArgumentTypeError(f"{p} is not a file.")
        return p

    def _is_char_device(p: Path) -> Path:
        if not p.is_char_device():
            raise ArgumentTypeError(f"{p} is not a character device.")
        return p

    def _existing_file(*fns: Callable[[Path], Path]) -> Callable[[str], Path]:
        def _check(s: str) -> Path:
            if not (p := Path(s)).exists():
                raise ArgumentTypeError(f"{p} not found.")
            return reduce(lambda p, fn: fn(p), fns, p)

        return _check

    parser = ArgumentParser(
        description="Expose the Tropic01 model API via a server.",
    )
    subparsers = parser.add_subparsers(title="Connection type")
    parser_tcp = subparsers.add_parser("tcp")
    parser_serial = subparsers.add_parser("serial")

    for subparser in (parser_tcp, parser_serial):
        subparser.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=0,
            help="Increase script verbosity, the more v's the more verbose.",
        )
        subparser.add_argument(
            "-c",
            "--configuration",
            type=_existing_file(_is_file, _with_ext(".yml", ".yaml")),
            help="Yaml file with the model configuration.",
            metavar="FILE",
        )

    parser_tcp.set_defaults(function=generate_tcp_connection)
    parser_tcp.add_argument(
        "-a",
        "--address",
        type=str,
        default=TCP_DEFAULT_ADDRESS,
        help="TCP address. Defaults to %(default)s.",
        metavar="STR",
    )
    parser_tcp.add_argument(
        "-p",
        "--port",
        type=int,
        default=TCP_DEFAULT_PORT,
        help="TCP port number. Defaults to %(default)s.",
        metavar="INT",
    )

    parser_serial.set_defaults(function=generate_serial_connection)
    parser_serial.add_argument(
        "-p",
        "--port",
        type=_existing_file(_is_char_device),
        default=SERIAL_DEFAULT_PORT,
        help="Serial port. Defaults to %(default)s.",
        metavar="FILE",
    )
    parser_serial.add_argument(
        "-b",
        "--baudrate",
        type=int,
        default=SERIAL_DEFAULT_BAUDRATE,
        help="Serial port baudrate. Defaults to %(default)s.",
        metavar="INT",
    )
    if kwargs := vars(parser.parse_args()):
        return kwargs
    parser.print_usage()


def main() -> None:
    if (kwargs := get_input_arguments()) is None:
        return
    configure_logging(kwargs["verbose"])
    kwargs["logger"] = logger = logging.getLogger("server")
    logger.debug("Arguments:%s", LogDict(kwargs))
    run_server(kwargs["function"](**kwargs), kwargs["configuration"], logger)


if __name__ == "__main__":
    main()
