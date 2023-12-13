# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
from typing import Iterable, List, TypeVar

T = TypeVar("T")


def sample_from(__iterable: Iterable[T], *, k: int) -> List[T]:
    return random.sample(list(__iterable), k=k)


def one_of(__iterable: Iterable[T]) -> T:
    return sample_from(__iterable, k=1)[0]


def sample_outside(
    __iterable: Iterable[int], /, nb_bytes: int = 1, *, k: int = 1
) -> List[int]:
    return random.sample(
        list(set(range(2 ** (nb_bytes * 8) - 1)) - set(__iterable)), k=k
    )


def one_outside(__iterable: Iterable[int], /, nb_bytes: int = 1) -> int:
    return sample_outside(__iterable, nb_bytes, k=1)[0]
