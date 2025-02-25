from contextlib import nullcontext
from typing import Any, ContextManager, Tuple

from typing_extensions import Self

from ..crypto.hash import crc16
from .datafield import AUTO, DataField, U8Scalar, U16Scalar, datafield
from .exceptions import UnauthorizedInstantiationError
from .message import Message


class L2Frame(Message):
    """Base class for L2 messages"""

    length: U8Scalar = datafield(is_data=False, default=AUTO)
    crc: U16Scalar = datafield(priority=999, is_data=False, default=AUTO)

    def set_length_if_auto(self) -> ContextManager[None]:
        """Update the LENGTH field of the message if set to AUTO."""
        if self.length.value is AUTO:
            return self.length.temporarily_set_to(
                sum(len(field) for _, field in self if field.params.is_data)
            )

        return nullcontext()

    def set_padding_if_auto(self) -> ContextManager[None]:
        """Fill the `padding` field of the message if set to AUTO."""
        try:
            padding_field: DataField[Any] = getattr(self, "padding")
        except AttributeError:
            return nullcontext()

        if padding_field.value is AUTO:
            return padding_field.temporarily_set_to([])

        return nullcontext()

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
        data, crc = self._get_data_and_crc()
        with self.crc.temporarily_set_to(crc):
            return data + self.crc.to_bytes()

    @property
    def data_field_bytes(self) -> bytes:
        with self.set_padding_if_auto():
            return super().data_field_bytes


class L2Request(L2Frame):
    """Base class for L2 messages sent to the TROPIC01"""

    id: U8Scalar = datafield(priority=-999, is_data=False, default=AUTO)

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        try:
            cls.ID
        except AttributeError:
            raise UnauthorizedInstantiationError(
                f"Instantiating {cls} forbidden: ID undefined."
            ) from None
        return super().__new__(cls)

    def set_id_if_auto(self) -> ContextManager[None]:
        """Update the ID field of the message if set to AUTO."""
        if self.id.value is AUTO:
            return self.id.temporarily_set_to(self.ID)
        return nullcontext()

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
