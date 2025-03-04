import logging
from contextlib import ExitStack
from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path
from typing import Any, ClassVar, NamedTuple, Optional, Protocol

from typing_extensions import Self

from ..protocols import TropicProtocol
from ..targets.model.tropic01_model import Tropic01Model
from .configuration import load_configuration

_BYTEORDER = "little"


def _to_bytes(__nb: int, __length: int) -> bytes:
    return __nb.to_bytes(__length, byteorder=_BYTEORDER)


def _from_bytes(__data: bytes) -> int:
    return int.from_bytes(__data, byteorder=_BYTEORDER)


@unique
class TagEnum(bytes, Enum):
    # TropicProtocol-related tags
    SPI_DRIVE_CSN_LOW = b"\x01"
    SPI_DRIVE_CSN_HIGH = b"\x02"
    SPI_SEND = b"\x03"
    POWER_ON = b"\x04"
    POWER_OFF = b"\x05"
    WAIT = b"\x06"
    # Target-related tag
    RESET_TARGET = b"\x10"
    # Error tags
    EXCEPTION = b"\xf0"
    """An exception occured during the processing by the target"""
    INVALID = b"\xfd"
    """Received tag is not part of the enumeration"""
    UNSUPPORTED = b"\xfe"
    """Server does not provide support for received tag"""


def instantiate_model(
    filepath: Optional[Path], logger: logging.Logger
) -> Tropic01Model:
    configuration = load_configuration(filepath, logger)
    return Tropic01Model.from_dict(configuration).set_logger(logging.getLogger("model"))


def enter_context(stack: ExitStack, target: TropicProtocol) -> TropicProtocol:
    stack.pop_all().close()
    stack.enter_context(target)
    return target


@dataclass
class Buffer:
    TAG_SIZE: ClassVar[int] = 1
    LENGTH_SIZE: ClassVar[int] = 2
    tag: bytes
    length: int = 0
    payload: bytes = b""

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        if (_l := len(data)) < (_m := cls.TAG_SIZE + cls.LENGTH_SIZE):
            raise RuntimeError(
                f"Should have received at least {_m} bytes; got {_l}. Report to development team."
            )
        return cls(
            tag=data[: (i := cls.TAG_SIZE)],
            length=_from_bytes(data[i : (i := i + cls.LENGTH_SIZE)]),
            payload=data[i:],
        )

    def to_bytes(self) -> bytes:
        return self.tag + _to_bytes(self.length, self.LENGTH_SIZE) + self.payload


class Connection(Protocol):
    def __enter__(self) -> Self:
        ...

    def __exit__(self, *args: Any) -> None:
        ...

    def connect(self) -> None:
        ...

    def receive(self, size: Optional[int] = None) -> bytes:
        ...

    def send(self, data: bytes) -> None:
        ...


def connect(connection: Connection) -> None:
    connection.connect()


def receive(connection: Connection, logger: logging.Logger) -> Optional[Buffer]:
    """Receive data from a socket and return a `Buffer` object."""

    def _receive(size: Optional[int] = None) -> bytes:
        rx = connection.receive(size)
        logger.debug("Received %d byte(s).", len(rx))
        logger.debug("%s.", rx)
        return rx

    if (rx := _receive()) == b"":
        return None

    buffer = Buffer.from_bytes(rx)

    logger.debug("Buffer length field = %(ln)d (%(ln)#x).", {"ln": buffer.length})
    expected_size = buffer.length + Buffer.TAG_SIZE + Buffer.LENGTH_SIZE
    logger.debug("Expected size: %d bytes.", expected_size)
    received_size = len(rx)
    logger.debug("Received size: %d bytes.", received_size)

    # Return if no more data are expected
    if (yet_to_receive := expected_size - received_size) <= 0:
        return buffer

    buffer.payload += _receive(yet_to_receive)
    if (_p := len(buffer.payload)) != (_l := buffer.length):
        raise RuntimeError(
            f"Payload size is {_p} bytes, should be {_l} bytes. Report to development team."
        )
    return buffer


def send(connection: Connection, buffer: Buffer, logger: logging.Logger) -> None:
    """Send the content of a `Buffer` object through a socket."""
    data = buffer.to_bytes()
    logger.debug("Sending %d byte(s).", len(data))
    logger.debug("Tx data: %s.", data)
    connection.send(data)


class ProcessingResult(NamedTuple):
    buffer: Buffer
    reset_target: bool = False


def process(
    buffer: Buffer, target: TropicProtocol, logger: logging.Logger
) -> ProcessingResult:
    """Process the received data."""

    # Check tag is known
    try:
        tag = TagEnum(buffer.tag)
    except ValueError as exc:
        logger.error(exc)
        return ProcessingResult(Buffer(TagEnum.INVALID))
    logger.debug("Tag: %r", tag)

    # choose command to execute depending on the tag's value.
    if tag is TagEnum.SPI_DRIVE_CSN_LOW:
        execute_command = lambda: target.spi_drive_csn_low()

    elif tag is TagEnum.SPI_DRIVE_CSN_HIGH:
        execute_command = lambda: target.spi_drive_csn_high()

    elif tag is TagEnum.SPI_SEND:
        execute_command = lambda: target.spi_send(buffer.payload)

    elif tag is TagEnum.POWER_ON:
        execute_command = lambda: target.power_on()

    elif tag is TagEnum.POWER_OFF:
        execute_command = lambda: target.power_off()

    elif tag is TagEnum.WAIT:
        wait_time = _from_bytes(buffer.payload)
        logger.debug("Wait time: %(wt)s (%(wt)#x)", {"wt": wait_time})
        execute_command = lambda: target.wait(wait_time)

    elif tag is TagEnum.RESET_TARGET:
        return ProcessingResult(Buffer(TagEnum.RESET_TARGET), reset_target=True)

    # No behaviour attached to the tag
    else:
        logger.warning("Tag %r is unsupported", tag)
        return ProcessingResult(Buffer(TagEnum.UNSUPPORTED))

    # Safely execute the command
    try:
        result = execute_command()
    except Exception as exc:
        logger.error("An exception occured in the target:", exc_info=exc)
        return ProcessingResult(Buffer(tag=TagEnum.EXCEPTION), reset_target=True)

    if result is None:
        result = b""

    # Return output data
    return ProcessingResult(Buffer(tag=tag, length=len(result), payload=result))


def run_server(
    connection: Connection, configuration: Optional[Path], logger: logging.Logger
) -> None:
    """Serve the Tropic01Model through the selected connection."""

    with connection, ExitStack() as stack:
        target = enter_context(stack, instantiate_model(configuration, logger))
        logger.info("Target instantiated.")

        while True:
            connect(connection)

            while (rx_buffer := receive(connection, logger)) is not None:
                logger.debug("Rx buffer: %s", rx_buffer)

                tx_buffer, reset_target = process(rx_buffer, target, logger)

                logger.debug("Tx buffer: %s", tx_buffer)
                send(connection, tx_buffer, logger)

                if reset_target:
                    target = enter_context(
                        stack, instantiate_model(configuration, logger)
                    )
                    logger.info("Target re-instantiated.")
