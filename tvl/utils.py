# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from itertools import islice
from typing import Iterable, Iterator, List, TypeVar

T = TypeVar("T")


def chunked(iterable: Iterable[T], n: int) -> Iterator[List[T]]:
    it = iter(iterable)
    while chunk := list(islice(it, n)):
        yield chunk


def split_data(data: bytes, *, chunk_size: int) -> Iterator[bytes]:
    """Split raw data into several chunks.

    Args:
        data (bytes): data to split
        chunk_size (int): Maximal size of an individual chunk

    Yields:
        the chunks
    """
    yield from map(bytes, chunked(data, chunk_size))
