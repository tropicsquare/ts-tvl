# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from contextlib import contextmanager, nullcontext
from typing import Any, ContextManager, Iterator, Tuple

from ..crypto.hash import crc16
from .datafield import AUTO, DataField, U8Scalar, U16Scalar, datafield
from .exceptions import UnauthorizedInstantiationError
from .message import Message


@contextmanager
def _restore(field: DataField[Any], value: int) -> Iterator[None]:
    """Context manager that restores the field value upon exit."""
    try:
        yield
    finally:
        field.value = value


class L2Frame(Message, is_base=True):
    """Base class for L2 messages"""

    length: U8Scalar = datafield(is_data=False, default=AUTO)
    crc: U16Scalar = datafield(priority=999, is_data=False, default=AUTO)

    def set_length_if_auto(self) -> ContextManager[None]:
        """Update the LENGTH field of the message if set to AUTO."""
        if (length_save := self.length.value) is AUTO:
            self.length.value = sum(
                len(field) for _, field in self if field.params.is_data
            )
        return _restore(self.length, length_save)

    def set_padding_if_auto(self) -> ContextManager[None]:
        """Fill the `padding` field of the message if set to AUTO."""
        try:
            padding_field = getattr(self, "padding")
        except AttributeError:
            return nullcontext()

        if (padding_save := padding_field.value) is AUTO:
            padding_field.value = []
        return _restore(padding_field, padding_save)

    def has_valid_crc(self) -> bool:
        """Check the CRC field of the message.

        Returns:
            True if the crc is valid, False otherwise
        """
        return self.crc.value is AUTO or self.crc.value == self.compute_crc()

    def update_crc(self) -> None:
        """Update crc of the message."""
        self.crc.value = self.compute_crc()

    def compute_crc(self) -> int:
        """Compute crc of the message.

        Returns:
            crc of the message
        """
        return self._get_data_and_crc(force_auto_crc=True)[1]

    def _get_data_and_crc(self, *, force_auto_crc: bool = False) -> Tuple[bytes, int]:
        with self.set_length_if_auto(), self.set_padding_if_auto():
            data = b"".join(field.to_bytes() for name, field in self if name != "crc")

            if (crc := self.crc.value) is AUTO or force_auto_crc:
                crc = crc16(data)

            return data, crc

    def to_bytes(self) -> bytes:
        """Serialize the message to bytes.

        Returns:
            bytes representation of the message
        """
        with _restore(self.crc, self.crc.value):
            data, self.crc.value = self._get_data_and_crc()
            return data + self.crc.to_bytes()

    @property
    def data_field_bytes(self) -> bytes:
        with self.set_padding_if_auto():
            return super().data_field_bytes


class L2Request(L2Frame):
    """Base class for L2 messages sent to the TROPIC01"""

    id: U8Scalar = datafield(priority=-999, is_data=False, default=AUTO)

    def __init__(self, **kwargs: Any) -> None:
        try:
            self.ID
        except AttributeError:
            raise UnauthorizedInstantiationError(
                f"Instantiating {self.__class__} forbidden: ID undefined."
            ) from None
        super().__init__(**kwargs)

    def set_id_if_auto(self) -> ContextManager[None]:
        """Update the ID field of the message if set to AUTO."""
        if (id_save := self.id.value) is AUTO:
            self.id.value = self.ID
        return _restore(self.id, id_save)

    def has_valid_id(self) -> bool:
        """Check if the ID field is valid.

        Returns:
            True if the instance id matches with that of the class
        """
        return self.id.value is AUTO or self.id.value == self.ID

    def _get_data_and_crc(self, *, force_auto_crc: bool = False) -> Tuple[bytes, int]:
        with self.set_id_if_auto():
            return super()._get_data_and_crc(force_auto_crc=force_auto_crc)


class L2Response(L2Frame):
    """Base class for L2 messages sent from the TROPIC01"""

    status: U8Scalar = datafield(priority=-999, is_data=False)
