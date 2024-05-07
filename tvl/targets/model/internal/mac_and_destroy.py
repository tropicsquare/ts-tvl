import os
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

from pydantic import BaseModel
from typing_extensions import Self

from tvl.crypto.conversion import bitlist_to_bytes, ints_to_bitlist
from tvl.crypto.kmac import kmac256
from tvl.targets.model.internal.generic_partition import (
    BaseSlot,
    GenericModel,
    GenericPartition,
)
from tvl.typing_utils import FixedSizeBytes

MACANDD_DATA_INPUT_LEN = 32
MACANDD_SLOT_BYTE_LEN = 1
MACANDD_KEY_LEN = 32
MACANDD_KEY_DEFAULT_VALUE = b"\xff" * MACANDD_KEY_LEN
MACANDD_KMAC_OUTPUT_LEN = 32


class MacAndDestroyError(Exception):
    pass


@dataclass
class MacAndDestroySlot(BaseSlot):
    value: bytes = field(default_factory=lambda: os.urandom(MACANDD_KMAC_OUTPUT_LEN))


class MacAndDestroySlots(GenericPartition[MacAndDestroySlot]):
    pass


@dataclass
class MacAndDestroyKey(BaseSlot):
    value: bytes = field(default=MACANDD_KEY_DEFAULT_VALUE)


class MacAndDestroyKeys(GenericPartition[MacAndDestroyKey]):
    pass


class MacAndDestroyData:
    def __init__(
        self,
        slots: Optional[MacAndDestroySlots] = None,
        keys: Optional[MacAndDestroyKeys] = None,
    ) -> None:
        self.slots = MacAndDestroySlots() if slots is None else slots
        self.keys = MacAndDestroyKeys() if keys is None else keys

    def read_slot(self, idx: int, *, erase: bool = False) -> bytes:
        slot = self.slots[idx]
        if erase:
            del self.slots[idx]
        return slot.value

    def write_slot(self, idx: int, value: bytes) -> None:
        self.slots[idx].value = value

    def read_key(self, idx: int) -> bytes:
        return self.keys[idx].value

    def write_key(self, idx: int, value: bytes) -> None:
        self.keys[idx].value = value

    def to_dict(self) -> Dict[int, Any]:
        return {
            "slots": self.slots.to_dict(),
            "keys": self.keys.to_dict(),
        }

    @classmethod
    def from_dict(cls, __mapping: Mapping[int, Any], /) -> Self:
        return cls(
            slots=MacAndDestroySlots.from_dict(__mapping.get("slots", {})),
            keys=MacAndDestroyKeys.from_dict(__mapping.get("keys", {})),
        )


def mac_and_destroy_kmac(key: bytes, data: bytes) -> bytes:
    return bitlist_to_bytes(
        kmac256(
            ints_to_bitlist(key),
            ints_to_bitlist(data),
            MACANDD_KMAC_OUTPUT_LEN * 8,
            ints_to_bitlist(b"My Tagged Application"),
        )
    )


class MacAndDestroyFunc:
    DATA_LEN: int

    def __init_subclass__(cls, *, data_len: int) -> None:
        cls.DATA_LEN = data_len

    def __init__(self, key: bytes) -> None:
        self.key = key
        self.data = b""

    def load(self, __data: bytes, /) -> Self:
        self.data += __data
        return self

    def compute(self) -> bytes:
        if (l := len(self.key)) != MACANDD_KEY_LEN:
            raise MacAndDestroyError(
                f"Key should be {MACANDD_KEY_LEN} byte long; is {l}."
            )
        if (l := len(self.data)) != self.DATA_LEN:
            raise MacAndDestroyError(
                f"Data should be {self.DATA_LEN} byte long: are {l}."
            )
        return mac_and_destroy_kmac(self.key, self.data)


class MacAndDestroyF1(
    MacAndDestroyFunc, data_len=MACANDD_DATA_INPUT_LEN + MACANDD_SLOT_BYTE_LEN
):
    pass


class MacAndDestroyF2(
    MacAndDestroyFunc,
    data_len=MACANDD_DATA_INPUT_LEN * 2 + MACANDD_SLOT_BYTE_LEN,
):
    pass


class MacAndDestroySlotModel(BaseModel):
    value: FixedSizeBytes[MACANDD_KMAC_OUTPUT_LEN]


class MacAndDestroySlotsModel(GenericModel):
    __root__: Dict[int, MacAndDestroySlotModel]


class MacAndDestroyKeyModel(BaseModel):
    value: FixedSizeBytes[MACANDD_KEY_LEN]


class MacAndDestroyKeysModel(GenericModel):
    __root__: Dict[int, MacAndDestroyKeyModel]


class MacAndDestroyDataModel(BaseModel):
    slots: Optional[MacAndDestroySlotsModel]
    keys: Optional[MacAndDestroyKeysModel]
