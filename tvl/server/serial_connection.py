import logging
from pathlib import Path
from typing import Any, Optional, Union, cast

from serial import Serial
from typing_extensions import Self

from .internal import run_server

SERIAL_DEFAULT_PORT = "/dev/ttyUSB0"
SERIAL_DEFAULT_BAUDRATE = 115200
SERIAL_BUFFER_SIZE = 3


class SerialConnection:
    def __init__(
        self, port: Union[Path, str], baudrate: int, logger: logging.Logger
    ) -> None:
        self.serial = Serial(str(port), baudrate)
        self.logger = logger
        self.logger.info("Serial comport created.")
        self.logger.debug("Serial port: %s; baudrate: %d", port, baudrate)

    def __enter__(self) -> Self:
        self.serial.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self.serial.__exit__(*args)

    def connect(self) -> None:
        pass

    def receive(self, size: Optional[int] = None) -> bytes:
        if size is None:
            size = SERIAL_BUFFER_SIZE
        self.logger.debug("Reading %d byte(s).", size)
        return self.serial.read(size)

    def send(self, data: bytes) -> None:
        to_send = len(data)
        # Make sure the data is transmitted in full
        while True:
            sent = cast(int, self.serial.write(data))
            if (to_send := to_send - sent) <= 0:
                return
            data = data[sent:]


def run_server_over_serial(
    port: Union[Path, str],
    baudrate: int,
    configuration: Optional[Path],
    logger: logging.Logger,
    **_: Any,
) -> None:
    run_server(
        SerialConnection(port, baudrate, logger),
        configuration,
        logger,
    )
