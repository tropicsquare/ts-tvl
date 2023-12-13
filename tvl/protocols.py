# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Protocol

from typing_extensions import Self


class TropicProtocol(Protocol):
    def __enter__(self) -> Self:
        ...

    def __exit__(self, *args: Any) -> None:
        ...

    def spi_drive_csn_low(self) -> None:
        """Drive the Chip Select signal to LOW."""
        ...

    def spi_drive_csn_high(self) -> None:
        """Drive the Chip Select signal to HIGH."""
        ...

    def spi_send(self, data: bytes) -> bytes:
        """Send data to the chip and receive as many bytes as response."""
        ...

    def power_on(self) -> None:
        """Power on the chip."""
        ...

    def power_off(self) -> None:
        """Power off the chip."""
        ...

    def wait(self, usecs: int) -> None:
        """Wait `usecs` microseconds in the chip time reference."""
        ...
