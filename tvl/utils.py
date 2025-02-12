# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from itertools import chain, islice
from typing import Iterable, Iterator, List, Type, TypeVar

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


def iter_subclasses(__cls: Type[T], /) -> Iterator[Type[T]]:
    """Iterate on the subclasses of a class

    Args:
        __cls (Type[T]): the class to scan

    Yields:
        the subclasses of the class
    """
    yield from __cls.__subclasses__()
    yield from chain.from_iterable(map(iter_subclasses, __cls.__subclasses__()))
