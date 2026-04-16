"""
TCP client implementing TropicProtocol, for talking to a tvl.server over TCP.

Each TropicProtocol method is translated to a tagged Buffer, sent to the
server, and the response Buffer's payload (if any) is returned.
"""

import logging
import socket
import subprocess
import time
from typing import Any, Optional

from typing_extensions import Self

from .internal import Buffer, TagEnum
from .tcp_connection import TCP_DEFAULT_ADDRESS, TCP_DEFAULT_PORT

# Size of the payload carrying the microsecond count for the WAIT tag.
# 4 bytes allows up to ~71 minutes of wait, more than enough for any realistic
# chip-time delay.
_WAIT_PAYLOAD_SIZE = 4


class TCPTropicProtocol:
    """
    TropicProtocol implementation that communicates with a tvl.server TCP model.

    If `server_process` is provided, the client polls its liveness around each
    I/O call and raises RuntimeError if the subprocess has exited, so that a
    dead server does not manifest as a silent `recv()` hang.
    """

    def __init__(
        self,
        address: str = TCP_DEFAULT_ADDRESS,
        port: int = TCP_DEFAULT_PORT,
        *,
        connection_timeout: float = 10.0,
        request_timeout: float = 10.0,
        server_process: "Optional[subprocess.Popen[Any]]" = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.address = address
        self.port = port
        self.connection_timeout = connection_timeout
        self.request_timeout = request_timeout
        self.server_process = server_process
        self._socket: Optional[socket.socket] = None
        self.logger = logger or logging.getLogger(self.__class__.__name__.lower())

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.disconnect()

    def connect(self) -> None:
        """Open a TCP connection to the server, retrying until the deadline."""
        if self._socket is not None:
            return

        deadline = time.monotonic() + self.connection_timeout
        last_err: Optional[BaseException] = None
        while True:
            self._check_server_alive()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            try:
                sock.connect((self.address, self.port))
            except (ConnectionRefusedError, socket.timeout, OSError) as exc:
                last_err = exc
                sock.close()
                if time.monotonic() >= deadline:
                    raise TimeoutError(
                        f"Could not connect to TCP model server at "
                        f"{self.address}:{self.port} within "
                        f"{self.connection_timeout}s (last error: {last_err!r})"
                    ) from last_err
                time.sleep(0.1)
                continue
            sock.settimeout(self.request_timeout)
            self._socket = sock
            self.logger.info("Connected to %s:%d", self.address, self.port)
            return

    def disconnect(self) -> None:
        """Close the TCP connection if open."""
        if self._socket is not None:
            self._socket.close()
            self._socket = None
            self.logger.info("Disconnected from server")

    # --- TropicProtocol interface -----------------------------------------

    def power_on(self) -> None:
        self._round_trip(TagEnum.POWER_ON)

    def power_off(self) -> None:
        self._round_trip(TagEnum.POWER_OFF)

    def spi_drive_csn_low(self) -> None:
        self._round_trip(TagEnum.SPI_DRIVE_CSN_LOW)

    def spi_drive_csn_high(self) -> None:
        self._round_trip(TagEnum.SPI_DRIVE_CSN_HIGH)

    def spi_send(self, data: bytes) -> bytes:
        return self._round_trip(TagEnum.SPI_SEND, data)

    def wait(self, usecs: int) -> None:
        self._round_trip(
            TagEnum.WAIT, usecs.to_bytes(_WAIT_PAYLOAD_SIZE, byteorder="little")
        )

    def irq_state(self) -> bool:
        # The TCP server processes every SPI request synchronously; by the time
        # a client polls for IRQ state, the response is already available.
        return True

    # --- internals --------------------------------------------------------

    def _round_trip(self, tag: TagEnum, payload: bytes = b"") -> bytes:
        self._send_buffer(Buffer(tag=tag, length=len(payload), payload=payload))
        return self._receive_buffer().payload

    def _send_buffer(self, buffer: Buffer) -> None:
        if self._socket is None:
            raise RuntimeError("Not connected to TCP server")
        self._check_server_alive()
        data = buffer.to_bytes()
        self.logger.debug("Sending: %s", data.hex())
        self._socket.sendall(data)

    def _receive_buffer(self) -> Buffer:
        if self._socket is None:
            raise RuntimeError("Not connected to TCP server")
        self._check_server_alive()

        header = self._recv_exact(Buffer.TAG_SIZE + Buffer.LENGTH_SIZE)
        tag = header[: Buffer.TAG_SIZE]
        length = int.from_bytes(header[Buffer.TAG_SIZE :], byteorder="little")
        payload = self._recv_exact(length) if length else b""
        buffer = Buffer(tag=tag, length=length, payload=payload)
        self.logger.debug("Received: %s", buffer.to_bytes().hex())
        return buffer

    def _recv_exact(self, n: int) -> bytes:
        assert self._socket is not None
        data = b""
        while len(data) < n:
            chunk = self._socket.recv(n - len(data))
            if not chunk:
                raise RuntimeError("Connection closed while receiving")
            data += chunk
        return data

    def _check_server_alive(self) -> None:
        if self.server_process is None:
            return
        if self.server_process.poll() is not None:
            raise RuntimeError(
                f"Server process terminated with code "
                f"{self.server_process.returncode}"
            )
