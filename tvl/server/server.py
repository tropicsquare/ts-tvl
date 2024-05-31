#!/usr/bin/env python3

import logging
from argparse import ArgumentParser, ArgumentTypeError
from contextlib import ExitStack
from dataclasses import dataclass
from enum import Enum, unique
from functools import lru_cache, reduce
from pathlib import Path
from pprint import pformat
from shutil import get_terminal_size
from socket import create_server, socket
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterable,
    NamedTuple,
    Optional,
    Protocol,
    Union,
    cast,
)

import yaml
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    load_der_private_key,
    load_der_public_key,
    load_pem_private_key,
    load_pem_public_key,
)
from cryptography.x509 import load_der_x509_certificate, load_pem_x509_certificate
from pydantic import root_validator  # type: ignore
from pydantic import BaseModel, Extra, FilePath, StrictBytes
from serial import Serial
from typing_extensions import Self

from tvl.configuration_file_model import ModelConfigurationModel
from tvl.protocols import TropicProtocol
from tvl.targets.model.tropic01_model import Tropic01Model

_LOGGER = logging.getLogger("server")

BYTEORDER = "little"

TCP_DEFAULT_ADDRESS = "127.0.0.1"
TCP_DEFAULT_PORT = 28992
TCP_BUFFER_SIZE = 1024

SERIAL_DEFAULT_PORT = "/dev/ttyUSB0"
SERIAL_DEFAULT_BAUDRATE = 115200
SERIAL_BUFFER_SIZE = 3

# TODO temporary solution, to be defined another way when flow is mature
DEFAULT_MODEL_CONFIG = {
    "i_pairing_keys": {
        0: {
            "value": b"\x83\xc36<\xff'G\xb7\xf7\xeb\x19\x85\x17c\x1aqTv\xb4\xfe\"F\x01E\x89\xc3\xac\x11\x8b\xb8\x9eQ"  # noqa E501
        }
    },
    "s_t_priv": b"H\xb9/\x05\x0b\xfb\x82@\"\xec\xef{\xc5\xec\xbc\xa4R\xd3\xfd'p\xe8\xb5T\x9e\x93g)\xacx\xc4m",  # noqa E501
    "s_t_pub": b"\x07z\xad\x06\x0b\xbb8F-:\xa5.\x9e\xef\xe8\xfa\xa7\x84\x16\x9b,g;\xe0n\xf3\xfe\x1f\xd1\xc1\x93G",  # noqa E501
}


def merge_dicts(*dcts: Dict[Any, Any]) -> Dict[Any, Any]:
    """Merge dictionaries, the first has the least priority."""

    def _combine_into(d: Dict[Any, Any], combined: Dict[Any, Any]) -> None:
        for k, v in d.items():
            if isinstance(v, dict):
                _combine_into(v, combined.setdefault(k, {}))  # type: ignore
            else:
                combined[k] = v

    result: Dict[Any, Any] = {}
    for dct in dcts:
        _combine_into(dct, result)
    return result


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


def _to_bytes(nb: int, *, nb_bytes: int) -> bytes:
    return nb.to_bytes(nb_bytes, byteorder=BYTEORDER)


def _from_bytes(data: bytes) -> int:
    return int.from_bytes(data, byteorder=BYTEORDER)


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


class KeyTypeError(TypeError):
    def __init__(self, key_type: str, type_: type, expected_type: type) -> None:
        super().__init__(f"{key_type} key type is not {expected_type}: {type_}")


class ConfigurationModel(BaseModel, extra=Extra.allow):
    """Pydantic model to validate the configuration file"""

    s_t_priv: Union[StrictBytes, FilePath]
    s_t_pub: Optional[Union[StrictBytes, FilePath]]
    x509_certificate: Union[StrictBytes, FilePath]

    @root_validator
    def process_values(cls, values: Dict[str, Union[bytes, Path]]):
        # process public key
        if (s_t_pub := values.get("s_t_pub")) is not None:
            if isinstance(s_t_pub, bytes):
                public_key = X25519PublicKey.from_public_bytes(s_t_pub)
            elif s_t_pub.suffix == ".pem":
                public_key = load_pem_public_key(s_t_pub.read_bytes())
            elif s_t_pub.suffix == ".der":
                public_key = load_der_public_key(s_t_pub.read_bytes())
            else:
                raise TypeError("Public key not in DER nor PEM format")

            if not isinstance(public_key, (expected := X25519PublicKey)):
                raise KeyTypeError("Public", type(public_key), expected)
            values["s_t_pub"] = public_key.public_bytes_raw()

        # process private key
        if (s_t_priv := values.get("s_t_priv")) is not None:
            if isinstance(s_t_priv, bytes):
                private_key = X25519PrivateKey.from_private_bytes(s_t_priv)
            elif s_t_priv.suffix == ".pem":
                private_key = load_pem_private_key(s_t_priv.read_bytes(), None)
            elif s_t_priv.suffix == ".der":
                private_key = load_der_private_key(s_t_priv.read_bytes(), None)
            else:
                raise TypeError("Private key not in DER nor PEM format")

            if not isinstance(private_key, (expected := X25519PrivateKey)):
                raise KeyTypeError("Private", type(private_key), expected)
            values["s_t_priv"] = private_key.private_bytes_raw()
            # define tropic public key if not defined
            if values.get("s_t_pub") is None:
                values["s_t_pub"] = private_key.public_key().public_bytes_raw()

        # process certificate
        if (cert := values.get("x509_certificate")) is not None:
            if isinstance(cert, Path):
                if cert.suffix == ".pem":
                    certificate = load_pem_x509_certificate(cert.read_bytes())
                elif cert.suffix == ".der":
                    certificate = load_der_x509_certificate(cert.read_bytes())
                else:
                    raise TypeError("Certificate not in DER nor PEM format")
                values["certificate"] = certificate.public_bytes(Encoding.DER)

        return values


@lru_cache
def load_configuration(filepath: Optional[Path]) -> Dict[Any, Any]:
    if filepath is None:
        config: Dict[Any, Any] = {}

    else:
        _LOGGER.info("Loading target configuration from %s.", filepath)
        config = yaml.safe_load(filepath.read_bytes())
        _LOGGER.debug("Configuration:%s", LogDict(config))
        # Checking file content
        config = ConfigurationModel.parse_obj(config).dict()

    # Merging file configuration with default configuration
    config = merge_dicts(DEFAULT_MODEL_CONFIG, config)
    _LOGGER.debug("Configuration after merge:%s", LogDict(config))

    # Checking configuration
    config = ModelConfigurationModel.parse_obj(config).dict(exclude_none=True)
    _LOGGER.debug("Validated configuration:%s", LogDict(config))
    _LOGGER.debug("STPUB[] = {%s};", LogIter(config["s_t_pub"], "%#04x"))
    _LOGGER.info("Target configuration loaded and validated.")
    return config


def instantiate_model(filepath: Optional[Path]) -> Tropic01Model:
    return Tropic01Model.from_dict(load_configuration(filepath)).set_logger(
        logging.getLogger("model")
    )


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
        assert (_l := len(data)) >= (
            _m := cls.TAG_SIZE + cls.LENGTH_SIZE
        ), f"Should have received at least {_m} bytes; got {_l}. Report to development team."
        return cls(
            tag=data[: (i := cls.TAG_SIZE)],
            length=_from_bytes(data[i : (i := i + cls.LENGTH_SIZE)]),
            payload=data[i:],
        )

    def to_bytes(self) -> bytes:
        return (
            self.tag + _to_bytes(self.length, nb_bytes=self.LENGTH_SIZE) + self.payload
        )


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


def receive(connection: Connection) -> Optional[Buffer]:
    """Receive data from a socket and return a `Buffer` object."""

    def _receive(size: Optional[int] = None) -> bytes:
        rx = connection.receive(size)
        _LOGGER.debug("Received %d byte(s).", len(rx))
        _LOGGER.debug("%s.", rx)
        return rx

    if (rx := _receive()) == b"":
        return None

    buffer = Buffer.from_bytes(rx)

    # Fill payload field of the buffer
    _LOGGER.debug("Buffer length = %(ln)d (%(ln)#x)", {"ln": buffer.length})

    if buffer.length == 0:
        return buffer

    rx = _receive(buffer.length)
    assert (
        _l := len(rx)
    ) > 0, f"Should have received a positive number of bytes, got {_l}. Report to development team."
    buffer.payload += rx
    assert (_p := len(buffer.payload)) == (
        _l := buffer.length
    ), f"Payload size is {_p} bytes, should be {_l} bytes. Report to development team."
    return buffer


def send(connection: Connection, buffer: Buffer) -> None:
    """Send the content of a `Buffer` object through a socket."""
    data = buffer.to_bytes()
    _LOGGER.debug("Sending %d byte(s).", len(data))
    _LOGGER.debug("Tx data: %s.", data)
    connection.send(data)


class TCPConnection:
    def __init__(self, address: str, port: int) -> None:
        self.server = create_server((address, port), backlog=1, reuse_port=True)
        self.client: socket
        _LOGGER.info("Server socket created.")
        _LOGGER.debug("Server address: %s", (address, port))

    def __enter__(self) -> Self:
        self.server.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self.server.__exit__(*args)

    def connect(self) -> None:
        _LOGGER.info("Listening for new connection.")
        self.client, client_address = self.server.accept()
        _LOGGER.info("New client connected.")
        _LOGGER.debug("New client address: %s", client_address)

    def change_buffer_size(self, size: int) -> None:
        pass

    def receive(self, size: Optional[int] = None) -> bytes:
        return self.client.recv(TCP_BUFFER_SIZE)

    def send(self, data: bytes) -> None:
        self.client.sendall(data)


class SerialConnection:
    def __init__(self, port: Union[Path, str], baudrate: int) -> None:
        self.serial = Serial(str(port), baudrate)
        _LOGGER.info("Serial comport created.")
        _LOGGER.debug("Serial port: %s; baudrate: %d", port, baudrate)

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
        _LOGGER.debug("Reading %d byte(s).", size)
        return self.serial.read(size)

    def send(self, data: bytes) -> None:
        to_send = len(data)
        # Make sure the data is transmitted in full
        while True:
            sent = cast(int, self.serial.write(data))
            if (to_send := to_send - sent) <= 0:
                return
            data = data[sent:]


class ProcessingResult(NamedTuple):
    buffer: Buffer
    reset_target: bool = False


def process(buffer: Buffer, target: TropicProtocol) -> ProcessingResult:
    """Process the received data."""
    # Check tag is known
    try:
        tag = TagEnum(buffer.tag)
    except ValueError as exc:
        _LOGGER.error(exc)
        return ProcessingResult(Buffer(TagEnum.INVALID))
    _LOGGER.debug("Tag: %s", tag)

    # Execute behaviour depending on the tag's value.
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
        _LOGGER.debug("Wait time: %(wt)s (%(wt)#x)", {"wt": wait_time})
        execute_command = lambda: target.wait(wait_time)

    elif tag is TagEnum.RESET_TARGET:
        return ProcessingResult(Buffer(TagEnum.RESET_TARGET), reset_target=True)

    # No behaviour attached to the tag
    else:
        return ProcessingResult(Buffer(TagEnum.UNSUPPORTED))

    # Safely execute the command
    try:
        result = execute_command()
    except Exception as exc:
        _LOGGER.error("An exception occured in the target:")
        _LOGGER.exception(exc)
        return ProcessingResult(Buffer(tag=TagEnum.EXCEPTION), reset_target=True)

    if result is None:
        result = b""

    # Return output data
    return ProcessingResult(Buffer(tag=tag, length=len(result), payload=result))


def run_server(
    connection: Connection,
    configuration: Optional[Path] = None,
) -> None:
    """Create a TCP server around the `Model`."""

    with connection, ExitStack() as stack:
        _LOGGER.info("Instantiating target.")
        target = enter_context(stack, instantiate_model(configuration))
        _LOGGER.info("Target instantiated.")

        while True:
            connect(connection)

            while (rx_buffer := receive(connection)) is not None:
                _LOGGER.debug("Rx buffer: %s", rx_buffer)

                _LOGGER.info("Processing received data.")
                tx_buffer, reset_target = process(rx_buffer, target)

                _LOGGER.info("Sending processed data.")
                _LOGGER.debug("Tx buffer: %s", tx_buffer)
                send(connection, tx_buffer)

                if reset_target:
                    _LOGGER.info("Resetting target.")
                    target = enter_context(stack, instantiate_model(configuration))
                    _LOGGER.info("Target re-instantiated.")


def generate_tcp_connection(**kwargs: Any) -> TCPConnection:
    return TCPConnection(kwargs["address"], kwargs["port"])


def generate_serial_connection(**kwargs: Any) -> SerialConnection:
    return SerialConnection(kwargs["port"], kwargs["baudrate"])


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
        f"./{Path(__file__).name}",
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
    return vars(parser.parse_args())


def configure_logging(verbose: int) -> None:
    try:
        level = [logging.WARNING, logging.INFO][verbose]
    except IndexError:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="[%(levelname)s] [%(name)s] %(message)s")


def main() -> None:
    kwargs = get_input_arguments()
    configure_logging(kwargs["verbose"])
    _LOGGER.debug("Arguments:%s", LogDict(kwargs))
    run_server(kwargs["function"](**kwargs), kwargs["configuration"])


if __name__ == "__main__":
    main()
