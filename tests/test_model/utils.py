import os
from random import getrandbits, randint, randrange, sample
from typing import Any, Iterable, Iterator, List, Optional, Sequence, TypeVar

import pytest

from tvl.crypto.ecdsa import P256_PARAMETERS
from tvl.targets.model.internal.configuration_object import (
    CONFIG_OBJECT_SIZE_BYTES,
    REGISTER_MASK,
    REGISTER_SIZE_BYTES,
)
from tvl.targets.model.internal.ecc_keys import KEY_SIZE, Origins
from tvl.targets.model.internal.mcounter import MCOUNTER_DEFAULT_VALUE, MCOUNTER_MAX_VAL
from tvl.targets.model.internal.user_data_partition import INIT_VALUE, SLOT_SIZE_BYTES

T = TypeVar("T")


def sample_from(__iterable: Iterable[T], *, k: int) -> List[T]:
    return sample(list(__iterable), k=k)


def one_of(__iterable: Iterable[T]) -> T:
    return sample_from(__iterable, k=1)[0]


def sample_outside(
    __iterable: Iterable[int], /, nb_bytes: int = 1, *, k: Optional[int] = None
) -> List[int]:
    _set = set(range(2 ** (nb_bytes * 8) - 1)) - set(__iterable)
    if k is None:
        k = len(_set)
    return sample(list(_set), k=k)


def one_outside(__iterable: Iterable[int], /, nb_bytes: int = 1) -> int:
    return sample_outside(__iterable, nb_bytes, k=1)[0]


def as_slow(data: Sequence[Any], not_slow_nb: int):
    """Mark some parameters as slow"""
    slow_marker = pytest.mark.slow
    not_slow_indices = set(sample(range(len(data)), k=not_slow_nb))
    for i, vector in enumerate(data):
        if i not in not_slow_indices:
            yield pytest.param(vector, marks=slow_marker, id=str(i))
        else:
            yield pytest.param(vector, id=str(i))


class UtilsEcc:
    VALID_INDICES = list(range(32))
    INVALID_INDICES = sorted(set(range(256)) - set(VALID_INDICES))

    @staticmethod
    def get_valid_ecdsa_private_key() -> bytes:
        return randint(1, P256_PARAMETERS.q - 1).to_bytes(KEY_SIZE, "big")

    @staticmethod
    def get_invalid_ecdsa_private_key() -> bytes:
        return randint(P256_PARAMETERS.q, 2 ** (KEY_SIZE * 8) - 1).to_bytes(
            KEY_SIZE, "big"
        )

    @staticmethod
    def get_ecdsa_key():  # type: ignore
        return {
            "d": os.urandom(KEY_SIZE),
            "w": os.urandom(KEY_SIZE),
            "a": os.urandom(KEY_SIZE * 2),
            "origin": one_of(Origins),
        }  # type: ignore

    @staticmethod
    def get_eddsa_key():  # type: ignore
        return {
            "s": os.urandom(KEY_SIZE),
            "prefix": os.urandom(KEY_SIZE),
            "a": os.urandom(KEY_SIZE),
            "origin": one_of(Origins),
        }  # type: ignore

    @classmethod
    def get_valid_data(cls):  # type: ignore
        if randint(0, 255) % 2 == 0:
            return cls.get_ecdsa_key()  # type: ignore
        return cls.get_eddsa_key()  # type: ignore


class UtilsMcounter:
    VALID_INDICES = list(range(16))
    INVALID_INDICES = sorted(set(range(256)) - set(VALID_INDICES))
    DEFAULT_VALUE = MCOUNTER_DEFAULT_VALUE

    @staticmethod
    def get_valid_data() -> int:
        return randint(0, MCOUNTER_MAX_VAL)

    @staticmethod
    def get_invalid_data() -> int:
        return randint(MCOUNTER_MAX_VAL + 1, 2**32 - 1)


class UtilsRMem:
    VALID_INDICES = list(range(512))
    INVALID_INDICES = sorted(set(range(65536)) - set(VALID_INDICES))
    INIT_VALUE = INIT_VALUE

    @staticmethod
    def get_valid_data() -> bytes:
        return os.urandom(randint(1, SLOT_SIZE_BYTES))


class UtilsCo:
    ADDR_MAX = 2**16

    @staticmethod
    def get_value() -> int:
        while (_value := getrandbits(REGISTER_SIZE_BYTES)) == REGISTER_MASK:
            continue
        return _value

    @classmethod
    def get_value_iter(cls) -> Iterator[int]:
        while True:
            yield cls.get_value()

    @staticmethod
    def valid_addresses() -> Iterator[int]:
        yield from range(0, CONFIG_OBJECT_SIZE_BYTES, REGISTER_SIZE_BYTES)

    @staticmethod
    def invalid_addresses_not_aligned(k: int) -> Iterator[int]:
        for _ in range(k):
            while (
                a := randint(1, CONFIG_OBJECT_SIZE_BYTES)
            ) % REGISTER_SIZE_BYTES == 0:
                continue
            yield a

    @classmethod
    def invalid_addresses_out_of_range_aligned(cls, k: int) -> Iterator[int]:
        for _ in range(k):
            while (
                a := randrange(CONFIG_OBJECT_SIZE_BYTES, cls.ADDR_MAX)
            ) % REGISTER_SIZE_BYTES != 0:
                continue
            yield a

    @classmethod
    def invalid_addresses_out_of_range_and_not_aligned(cls, k: int) -> Iterator[int]:
        for _ in range(k):
            while (
                a := randrange(CONFIG_OBJECT_SIZE_BYTES, cls.ADDR_MAX)
            ) % REGISTER_SIZE_BYTES == 0:
                continue
            yield a
