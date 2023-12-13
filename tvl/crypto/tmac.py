# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from typing import List

from .conversion import bit, bitlist_to_bytes, ints_to_bitlist
from .keccak import keccak_f, pad10s1, sponge


def _keccak_tmac(x: List[bit]) -> List[bit]:
    """TropicSquare's custom sponge function"""
    return sponge(keccak_f(400), pad10s1, 144)(x, 256)


def tmac(key: bytes, data: bytes, nonce: bytes) -> bytes:
    """TMAC computation function"""
    new_x = nonce + bytes([len(key)]) + key + b"\x00\x00" + data
    return bitlist_to_bytes(_keccak_tmac(ints_to_bitlist(new_x) + [bit(0), bit(0)]))
