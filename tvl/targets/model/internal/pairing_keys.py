from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Mapping

from pydantic import BaseModel, root_validator
from typing_extensions import Self

from ....typing_utils import SizedBytes
from .generic_partition import BaseSlot, GenericModel, GenericPartition

KEY_SIZE = 32


class PairingKeysError(Exception):
    ...


class BlankSlotError(PairingKeysError):
    pass


class WrittenSlotError(PairingKeysError):
    ...


class InvalidatedSlotError(PairingKeysError):
    pass


class SlotState(str, Enum):
    BLANK = "blank"
    WRITTEN = "written"
    INVALID = "invalid"

    __str__ = str.__str__


@dataclass
class PairingKeySlot(BaseSlot):
    """Pairing key"""

    value: bytes = b""
    state: SlotState = SlotState.BLANK

    def __post_init__(self) -> None:
        # Enforce state attribute being enumerated.
        # `from_dict` method might initialize slot with str.
        self.state = SlotState(self.state)

    def write(self, value: bytes) -> None:
        """Write a new value.

        Args:
            value (bytes): the pairing key value

        Raises:
            ValueError: value must be a KEY_SIZE-long array of bytes
            WrittenSlotError: slot is already written and therefore not writable
        """
        if (ln := len(value)) != KEY_SIZE:
            raise ValueError(f"Pairing key size must be {KEY_SIZE}: got {ln}.")
        if self.state is not SlotState.BLANK:
            raise WrittenSlotError("Pairing key slot is already written.")
        self.state = SlotState.WRITTEN
        self.value = value

    def read(self) -> bytes:
        """Read the value of the pairing key.

        Returns:
            the value of the pairing key

        Raises:
            BlankSlotError: slot is blank and therefore not readable
            InvalidatedSlotError: slot is invalidated and therefore not readable
        """
        if self.state is SlotState.BLANK:
            raise BlankSlotError("Pairing key slot is blank.")
        if self.state is SlotState.INVALID:
            raise InvalidatedSlotError("Pairing key slot is invalidated.")
        return self.value

    def invalidate(self) -> None:
        """Invalidate the the pairing key slot.

        Raises:
            BlankSlotError: slot is blank and therefore not erasable
        """
        if self.state is SlotState.BLANK:
            raise BlankSlotError("Pairing key slot is blank.")
        self.state = SlotState.INVALID
        self.value = b""

    def is_valid(self) -> bool:
        return self.state is SlotState.WRITTEN

    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value, "state": self.state.value}

    @classmethod
    def from_dict(cls, __mapping: Mapping[str, Any], /) -> Self:
        value = __mapping.get("value")

        if value is not None and __mapping.get("state") is None:
            return super().from_dict(
                {
                    "value": value,
                    "state": SlotState.WRITTEN,
                }
            )

        return super().from_dict(__mapping)


class PairingKeys(GenericPartition[PairingKeySlot]):
    """Pairing keys partition"""


class PairingKeySlotModel(BaseModel):
    # Blank and invalidated slots hold no value, so an empty `value` has to be
    # accepted - a stricter field would reject the configuration dumped by the
    # model after a pairing key invalidation. The field cannot express "empty or
    # KEY_SIZE-long", so the sizes are checked in `_check_value_matches_state`.
    value: SizedBytes[0, KEY_SIZE] = b""
    state: SlotState = SlotState.WRITTEN

    @root_validator(skip_on_failure=True)
    def _check_value_matches_state(cls, values: Dict[str, Any]):  # noqa: N805
        ln = len(values.get("value", b""))
        if ln not in (0, KEY_SIZE):
            raise ValueError(f"A pairing key size must be 0 or {KEY_SIZE}: got {ln}.")
        if values.get("state") is SlotState.WRITTEN and ln != KEY_SIZE:
            raise ValueError(
                f"A written pairing key size must be {KEY_SIZE}: got {ln}."
            )
        return values


class PairingKeysModel(GenericModel):
    __root__: Dict[int, PairingKeySlotModel]
