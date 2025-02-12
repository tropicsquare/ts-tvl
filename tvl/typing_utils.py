# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from enum import IntEnum
from typing import Tuple, Type, TypeVar

from pydantic import conbytes, conint, conlist

T = TypeVar("T")


class SizedBytes:
    """
    Type hint that specifies size-constrained bytes

    Args:
        min_size (int): minimum size
        max_size (int): maximum size
    """

    def __class_getitem__(cls, param: Tuple[int, int]):
        mn, mx = param
        return conbytes(strict=True, min_length=mn, max_length=mx)


class FixedSizeBytes:
    """
    Type hint that specifies fixed-size bytes

    Args:
        size (int): fixed size
    """

    def __class_getitem__(cls, size: int):
        return SizedBytes[size, size]


class RangedInt:
    """
    Type hint that specifies ranged integers

    Args:
        min_value (int): minimum value - included in range
        max_value (int): maximum value - included in range
    """

    def __class_getitem__(cls, param: Tuple[int, int]):
        mn, mx = param
        return conint(strict=True, ge=mn, le=mx)


class SizedList:
    """
    Type hint that specifies size-constrained lists

    Args:
        item_type (type): type of items in list
        min_size (int): minimum size
        max_size (int): maximum size
    """

    def __class_getitem__(cls, param: Tuple[Type[T], int, int]):
        tp, mn, mx = param
        return conlist(tp, min_items=mn, max_items=mx)


class HexReprIntEnum(IntEnum):
    """Represents enumerated integers in hexadecimal"""

    def __repr__(self) -> str:
        return f"<{self!s}: {self.value:#x}>"
