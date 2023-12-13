# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import Dict

from pydantic import BaseModel

from ....typing import RangedInt
from .generic_partition import BaseSlot, GenericModel, GenericPartition

MCOUNTER_SIZE = 24
MCOUNTER_MAX_VAL = 2**MCOUNTER_SIZE - 1
MCOUNTER_MIN_VAL = 0
NOTSET_VALUE = -1


class MCounterError(Exception):
    pass


class MCounterWrongInitValueError(MCounterError):
    pass


class MCounterNotInitializedError(MCounterError):
    pass


class MCounterUpdateError(MCounterError):
    pass


@dataclass
class MCounter(BaseSlot):
    """Monotonic counter"""

    value: int = NOTSET_VALUE

    def init(self, value: int) -> None:
        """Initialize a new monotonic counter.

        Args:
            value (int): the value of the counter

        Raises:
            MCounterWrongInitValueError: bad init value
        """
        if not MCOUNTER_MIN_VAL <= value <= MCOUNTER_MAX_VAL:
            raise MCounterWrongInitValueError(
                f"Value out of range: [{MCOUNTER_MIN_VAL}:{MCOUNTER_MAX_VAL}]."
            )
        self.value = value

    def update(self) -> None:
        """Update the value of the monotonic counter.

        Raises:
            MCounterNotInitializedError: the counter is not initialized
            MCounterUpdateError: impossible to update the counter
        """
        if self.value == NOTSET_VALUE:
            raise MCounterNotInitializedError("Counter not initialized yet.")
        if self.value <= MCOUNTER_MIN_VAL:
            raise MCounterUpdateError(
                f"Unable to decrement counter beyond {MCOUNTER_MIN_VAL}."
            )
        self.value -= 1

    def get(self) -> int:
        """Get the value of the monotonic counter.

        Raises:
            MCounterNotInitializedError: the counter is not initialized

        Returns:
            the value of the counter
        """
        if self.value == NOTSET_VALUE:
            raise MCounterNotInitializedError("Counter not initialized yet.")
        return self.value


class MCounters(GenericPartition[MCounter]):
    """Monotonic counters partition"""


class MCounterModel(BaseModel):
    value: RangedInt[MCOUNTER_MIN_VAL, MCOUNTER_MAX_VAL]


class MCountersModel(GenericModel):
    __root__: Dict[int, MCounterModel]
