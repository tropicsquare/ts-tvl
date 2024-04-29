import os
from dataclasses import dataclass, field
from typing import Dict

from pydantic import BaseModel
from tvl.crypto.conversion import bitlist_to_bytes, ints_to_bitlist
from tvl.crypto.kmac import kmac256
from tvl.targets.model.internal.generic_partition import (
    BaseSlot,
    GenericModel,
    GenericPartition,
)
from tvl.typing_utils import FixedSizeBytes
from typing_extensions import Self

MACANDD_DATA_INPUT_LEN = 32
MACANDD_SLOT_BYTE_LEN = 1
MACANDD_KEY_LEN = 32
MACANDD_KMAC_OUTPUT_LEN = 32


class MacAndDestroyError(Exception):
    pass


@dataclass
class MacAndDestroySlot(BaseSlot):
    value: bytes = field(
        default_factory=lambda: os.urandom(MACANDD_KMAC_OUTPUT_LEN)
    )


class MacAndDestroyData(GenericPartition[MacAndDestroySlot]):
    def read_slot(self, idx: int, *, erase: bool = False) -> bytes:
        slot = self[idx]
        if erase:
            del self[idx]
        return slot.value

    def write_slot(self, idx: int, value: bytes) -> None:
        self[idx].value = value


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


class MacAndDestroyDataModel(GenericModel):
    __root__: Dict[int, MacAndDestroySlotModel]
