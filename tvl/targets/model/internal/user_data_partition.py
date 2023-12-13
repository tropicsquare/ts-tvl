# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import Dict

from pydantic import BaseModel, StrictBool

from ....typing import SizedBytes
from .generic_partition import BaseSlot, GenericModel, GenericPartition

SLOT_SIZE_BYTES = 444
INIT_VALUE = b"\xFF" * SLOT_SIZE_BYTES


class UserDataError(Exception):
    pass


class DataLengthOverflow(UserDataError):
    pass


class SlotAlreadyWrittenError(UserDataError):
    pass


@dataclass
class UserDataSlot(BaseSlot):
    """User-data slot"""

    free: bool = True
    value: bytes = INIT_VALUE

    def erase(self) -> None:
        """Erase the content of the slot"""
        self.free = True
        self.value = INIT_VALUE

    def read(self) -> bytes:
        """Read the data in the slot.

        Returns:
            the data contained in the slot
        """
        return self.value

    def write(self, value: bytes) -> None:
        """Write data in the slot

        Args:
            value (bytes): data to write

        Raises:
            SlotAlreadyWrittenError: some data are already in the slot
            DataLengthOverflow: too much data to fit in the slot
        """
        if not self.free:
            raise SlotAlreadyWrittenError(
                "Slot already written, erase before writing again."
            )
        if len(value) > SLOT_SIZE_BYTES:
            raise DataLengthOverflow(f"Slot max size is {SLOT_SIZE_BYTES}.")
        self.free = False
        if value:
            self.value = value


class UserDataPartition(GenericPartition[UserDataSlot]):
    """User-data partition"""


class UserDataSlotModel(BaseModel):
    free: StrictBool = False
    value: SizedBytes[0, SLOT_SIZE_BYTES]


class UserDataPartitionModel(GenericModel):
    __root__: Dict[int, UserDataSlotModel]
