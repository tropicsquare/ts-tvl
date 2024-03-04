# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
import random
from typing import Iterable, List, Optional, TypeVar

from tvl.targets.model.internal.ecc_keys import KEY_SIZE, Origins
from tvl.targets.model.internal.mcounter import MCOUNTER_MAX_VAL, NOTSET_VALUE
from tvl.targets.model.internal.user_data_partition import INIT_VALUE, SLOT_SIZE_BYTES

T = TypeVar("T")


def sample_from(__iterable: Iterable[T], *, k: int) -> List[T]:
    return random.sample(list(__iterable), k=k)


def one_of(__iterable: Iterable[T]) -> T:
    return sample_from(__iterable, k=1)[0]


def sample_outside(
    __iterable: Iterable[int], /, nb_bytes: int = 1, *, k: Optional[int] = None
) -> List[int]:
    _set = set(range(2 ** (nb_bytes * 8) - 1)) - set(__iterable)
    if k is None:
        k = len(_set)
    return random.sample(list(_set), k=k)


def one_outside(__iterable: Iterable[int], /, nb_bytes: int = 1) -> int:
    return sample_outside(__iterable, nb_bytes, k=1)[0]


class UtilsEcc:
    VALID_INDICES = list(range(1, 33))
    INVALID_INDICES = sorted(set(range(256)) - set(VALID_INDICES))

    @staticmethod
    def get_ecdsa_key():
        return {
            "d": os.urandom(KEY_SIZE),
            "w": os.urandom(KEY_SIZE),
            "a": os.urandom(KEY_SIZE * 2),
            "origin": one_of(Origins),
        }

    @staticmethod
    def get_eddsa_key():
        return {
            "s": os.urandom(KEY_SIZE),
            "prefix": os.urandom(KEY_SIZE),
            "a": os.urandom(KEY_SIZE),
            "origin": one_of(Origins),
        }

    @classmethod
    def get_valid_data(cls):
        if random.randint(0, 255) % 2 == 0:
            return cls.get_ecdsa_key()
        return cls.get_eddsa_key()


class UtilsMcounter:
    VALID_INDICES = list(range(1, 17))
    INVALID_INDICES = sorted(set(range(256)) - set(VALID_INDICES))
    NOTSET_VALUE = NOTSET_VALUE

    @staticmethod
    def get_valid_data() -> int:
        return random.randint(0, MCOUNTER_MAX_VAL)

    @staticmethod
    def get_invalid_data() -> int:
        return random.randint(MCOUNTER_MAX_VAL + 1, 2**32 - 1)


class UtilsRMem:
    VALID_INDICES = list(range(1, 513))
    INVALID_INDICES = sorted(set(range(65536)) - set(VALID_INDICES))
    INIT_VALUE = INIT_VALUE

    @staticmethod
    def get_valid_data() -> bytes:
        return os.urandom(random.randint(1, SLOT_SIZE_BYTES))
