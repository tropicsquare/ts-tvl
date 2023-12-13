# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from itertools import islice
from typing import Iterable, Iterator, List, TypeVar

T = TypeVar("T")


def chunked(iterable: Iterable[T], n: int) -> Iterator[List[T]]:
    it = iter(iterable)
    while chunk := list(islice(it, n)):
        yield chunk
