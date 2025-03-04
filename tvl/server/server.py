#!/usr/bin/env python3

import logging
from argparse import ArgumentParser, ArgumentTypeError, RawDescriptionHelpFormatter
from functools import reduce
from pathlib import Path
from textwrap import dedent
from typing import Callable

from .logging_utils import LogDict, configure_logging, dump_logging_configuration
from .serial_connection import (
    SERIAL_DEFAULT_BAUDRATE,
    SERIAL_DEFAULT_PORT,
    run_server_over_serial,
)
from .tcp_connection import TCP_DEFAULT_ADDRESS, TCP_DEFAULT_PORT, run_server_over_tcp


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
    # subparsers = parser.add_subparsers(title="Connection type")
    subparsers = parser.add_subparsers(required=True)
    parser_tcp = subparsers.add_parser(
        "tcp", description="Serve the Tropic01 model via TCP/IP."
    )
    parser_serial = subparsers.add_parser(
        "serial", description="Serve the Tropic01 model via serial port."
    )
    parser_dump_logging_cfg = subparsers.add_parser(
        "dump-logging-cfg",
        formatter_class=RawDescriptionHelpFormatter,
        description=dedent(
            """\
            Dump the default logging configuration in YAML format.
            The configuration can then be reused via the argument '--logging-configuration'.
        """
        ),
    )

    for subparser in (parser_tcp, parser_serial):
        subparser.add_argument(
            "-c",
            "--configuration",
            type=_existing_file(_is_file, _with_ext(".yml", ".yaml")),
            help="Yaml file with the model configuration.",
            metavar="FILE",
        )
        subparser.add_argument(
            "-l",
            "--logging-configuration",
            type=_existing_file(_is_file, _with_ext(".yml", ".yaml")),
            help="Yaml file with the logging configuration.",
            metavar="FILE",
        )

    parser_tcp.set_defaults(function=run_server_over_tcp)
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

    parser_serial.set_defaults(function=run_server_over_serial)
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

    parser_dump_logging_cfg.set_defaults(function=dump_logging_configuration)

    return vars(parser.parse_args())


def main() -> None:
    kwargs = get_input_arguments()
    configure_logging(kwargs.get("logging_configuration"))
    kwargs["logger"] = logger = logging.getLogger("server")
    logger.debug("Arguments:%s", LogDict(kwargs))
    kwargs["function"](**kwargs)


if __name__ == "__main__":
    main()
