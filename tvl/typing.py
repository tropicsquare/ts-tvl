from typing import Tuple

from pydantic import conbytes, conint


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
