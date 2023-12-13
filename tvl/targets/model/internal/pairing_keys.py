# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import Dict

from pydantic import BaseModel

from ....typing import FixedSizeBytes
from .generic_partition import BaseSlot, GenericModel, GenericPartition

KEY_SIZE = 32
BLANK_VALUE = b"\xFF" * KEY_SIZE
INVALID_VALUE = b"\x00" * KEY_SIZE


class InvalidatedSlotError(Exception):
    pass


@dataclass
class PairingKeySlot(BaseSlot):
    """Pairing key"""

    value: bytes = BLANK_VALUE

    def write(self, value: bytes) -> None:
        """Write a new value.

        Args:
            value (bytes): the pairing key value

        Raises:
            ValueError: value must be a KEY_SIZE-long array of bytes
            InvalidatedSlotError: slot is invalidated and therefore not usable
        """
        if (ln := len(value)) != KEY_SIZE:
            raise ValueError(f"Pairing key size must be {KEY_SIZE}: got {ln}.")
        if self.is_invalidated():
            raise InvalidatedSlotError("Pairing key slot is invalidated.")
        self.value = (
            int.from_bytes(self.value, byteorder="big")
            & int.from_bytes(value, byteorder="big")
        ).to_bytes(KEY_SIZE, byteorder="big")

    def read(self) -> bytes:
        """Read the value of the pairing key.

        Returns:
            the value of the pairing key
        """
        return self.value

    def is_blank(self) -> bool:
        """Assess whether the slot is blank.

        Returns:
            True if slot is blank, False otherwise
        """
        return self.value == BLANK_VALUE

    def is_invalidated(self) -> bool:
        """Assess whether the key is invalidated.

        Returns:
            True is key is invalidated, False otherwise
        """
        return self.value == INVALID_VALUE


class PairingKeys(GenericPartition[PairingKeySlot]):
    """Pairing keys partition"""


class PairingKeySlotModel(BaseModel):
    value: FixedSizeBytes[KEY_SIZE]


class PairingKeysModel(GenericModel):
    __root__: Dict[int, PairingKeySlotModel]
