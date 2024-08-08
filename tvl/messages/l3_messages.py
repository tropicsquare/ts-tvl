# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from contextlib import nullcontext
from typing import Any, ContextManager, Type

from typing_extensions import Self

from .datafield import AUTO, U8Array, U8Scalar, U16Scalar, datafield
from .exceptions import UnauthorizedInstantiationError
from .message import BaseMessage, Message

TAG_LEN = 16


class MinNbBytesDescriptor:
    def __get__(self, _, owner: Type["L3EncryptedPacket"]) -> int:
        return sum(
            params.dtype.nb_bytes * params.min_size
            for name, _, params in owner.specs()
            if name in ("size", "tag")
        )


class L3EncryptedPacket(BaseMessage):
    """Utility class to parse encrypted messages"""

    size: U16Scalar = datafield(is_data=False)
    ciphertext: U8Array = datafield(min_size=0, max_size=2**16 - 1)
    tag: U8Array = datafield(size=TAG_LEN)
    MIN_NB_BYTES = MinNbBytesDescriptor()

    @classmethod
    def from_encrypted(cls, __data: bytes, /) -> Self:
        """Parse encrypted data and create a encrypted packet object"""
        return cls(
            ciphertext=(ciphertext := __data[:-TAG_LEN]),
            tag=__data[-TAG_LEN:],
            size=len(ciphertext),
        )


class L3Packet(Message, is_base=True):
    """Base class for L3 messages"""

    def set_padding_if_auto(self) -> ContextManager[None]:
        """Fill the `padding` field of the message if set to AUTO."""
        try:
            padding_field = getattr(self, "padding")
        except AttributeError:
            return nullcontext()

        if (padding_save := padding_field.value) is AUTO:
            padding_field.value = []
        return self._restore(padding_field, padding_save)

    def to_bytes(self) -> bytes:
        with self.set_padding_if_auto():
            return super().to_bytes()


class L3Command(L3Packet):
    """Base class for L3 messages sent to the TROPIC01"""

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
        return self._restore(self.id, id_save)

    def has_valid_id(self) -> bool:
        """Check if the ID field is valid.

        Returns:
            True if the instance id matches with that of the class
        """
        return self.id.value is AUTO or self.id.value == self.ID

    def to_bytes(self) -> bytes:
        with self.set_id_if_auto():
            return super().to_bytes()


class L3Result(L3Packet):
    """Base class for L3 messages sent from the TROPIC01"""

    result: U8Scalar = datafield(priority=-999, is_data=False)
