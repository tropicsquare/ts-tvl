from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Mapping

from pydantic import BaseModel, StrictBytes, validator
from typing_extensions import Self

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
    value: StrictBytes = b""
    state: SlotState = SlotState.WRITTEN

    @validator("state")
    def _check_value_matches_state(  # noqa: N805
        cls, state: SlotState, values: Dict[str, Any]
    ) -> SlotState:
        # `value` is absent from `values` if it already failed validation.
        if (value := values.get("value")) is None:
            return state
        if state is SlotState.WRITTEN:
            if (ln := len(value)) != KEY_SIZE:
                raise ValueError(
                    f"a written pairing key must be {KEY_SIZE} bytes long: got {ln}"
                )
        elif value:
            raise ValueError(f"a {state} pairing key slot must have an empty value")
        return state


class PairingKeysModel(GenericModel):
    __root__: Dict[int, PairingKeySlotModel]
