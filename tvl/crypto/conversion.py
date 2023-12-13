# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from itertools import chain
from typing import Iterable, List, NewType

from ..utils import chunked

bit = NewType("bit", int)


def int_to_bitlist(n: int, nb_bits: int = 8) -> List[bit]:
    """Turn byte into a list of bits"""
    return [bit((n >> i) & 1) for i in range(nb_bits)]


def ints_to_bitlist(__b: Iterable[int], /) -> List[bit]:
    """Turn bytes into a list of bits"""
    return list(chain.from_iterable(int_to_bitlist(byte) for byte in __b))


def bitlist_to_int(r: Iterable[bit]) -> int:
    """Turn a list of bits into an integer"""
    return sum(bit * (2**i) for i, bit in enumerate(r))


def bitlist_to_bytes(__l: Iterable[bit], /) -> bytes:
    """Turn a list of bits into bytes"""
    return bytes(bitlist_to_int(chunk) for chunk in chunked(__l, 8))
