import logging
from socket import create_server, socket
from typing import Any, Optional

from typing_extensions import Self

TCP_DEFAULT_ADDRESS = "127.0.0.1"
TCP_DEFAULT_PORT = 28992
TCP_BUFFER_SIZE = 1024


class TCPConnection:
    def __init__(self, address: str, port: int, logger: logging.Logger) -> None:
        self.server = create_server((address, port), backlog=1, reuse_port=True)
        self.client: socket
        self.logger = logger
        self.logger.info("Server socket created.")
        self.logger.debug("Server address: %s", (address, port))

    def __enter__(self) -> Self:
        self.server.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self.server.__exit__(*args)

    def connect(self) -> None:
        self.logger.info("Listening for new connection.")
        self.client, client_address = self.server.accept()
        self.logger.info("New client connected.")
        self.logger.debug("New client address: %s", client_address)

    def change_buffer_size(self, size: int) -> None:
        pass

    def receive(self, size: Optional[int] = None) -> bytes:
        if size is None:
            return self.client.recv(TCP_BUFFER_SIZE)

        self.logger.debug("Expecting %d byte(s).", size)
        data = b""
        while len(data) < size:
            data += self.client.recv(TCP_BUFFER_SIZE)
            self.logger.debug("Already got %d byte(s).", len(data))
        return data

    def send(self, data: bytes) -> None:
        self.client.sendall(data)


def generate_tcp_connection(**kwargs: Any) -> TCPConnection:
    return TCPConnection(kwargs["address"], kwargs["port"], kwargs["logger"])
