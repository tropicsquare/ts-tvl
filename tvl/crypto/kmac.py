# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from typing import List, Tuple

from ..utils import chunked
from .conversion import bit, int_to_bitlist, ints_to_bitlist
from .keccak import keccak_c, shake256

"""cSHAKE and KMAC as per https://doi.org/10.6028/NIST.SP.800-185"""


def _encode(__x: int, /) -> Tuple[List[bit], List[bit]]:
    if (nb_bytes := (__x.bit_length() + 7) // 8) == 0:
        nb_bytes = 1

    reversed_bytes: List[bit] = []
    for bits in chunked(int_to_bitlist(__x, nb_bytes * 8), 8):
        reversed_bytes = bits + reversed_bytes

    return int_to_bitlist(nb_bytes, 8), reversed_bytes


def left_encode(x: int) -> List[bit]:
    """left_encode function as defined in NIST.SP.800-185 2.3.1"""
    encoded_nb_bytes, encoded_x = _encode(x)
    return encoded_nb_bytes + encoded_x


def right_encode(x: int) -> List[bit]:
    """right_encode function as defined in NIST.SP.800-185 2.3.1"""
    encoded_nb_bytes, encoded_x = _encode(x)
    return encoded_x + encoded_nb_bytes


def encode_string(s: List[bit]) -> List[bit]:
    """encode_string function as defined in NIST.SP.800-185 2.3.2"""
    return left_encode(len(s)) + s


def bytepad(x: List[bit], w: int) -> List[bit]:
    """bytepad function as defined in NIST.SP.800-185 2.3.3"""
    z = left_encode(w) + x
    w_bits = w * 8
    z += [bit(0)] * ((w_bits - len(z) % w_bits) % w_bits)
    return z


def cshake256(x: List[bit], l: int, n: List[bit], s: List[bit]) -> List[bit]:
    """cSHAKE256 function as defined in NIST.SP.800-185 3.3

    Args:
        x (List[bit]): main input bit string
        l (int): output length in bits
        n (List[bit]): function-name bit string
        s (List[bit]): customization bit string

    Returns:
        output bit string
    """
    if n or s:
        new_n = bytepad(encode_string(n) + encode_string(s), 136) + x + [bit(0), bit(0)]
        return keccak_c(512)(new_n, l)
    return shake256(x, l)


def kmac256(k: List[bit], x: List[bit], l: int, s: List[bit]) -> List[bit]:
    """KMAC256 function as defined in NIST.SP.800-185 4.3

    Args:
        k (List[bit]): key bit string
        x (List[bit]): main input bit string
        l (int): output length in bits
        s (List[bit]): customization bit string

    Returns:
        output bit string
    """
    new_x = bytepad(encode_string(k), 136) + x + right_encode(l)
    return cshake256(new_x, l, ints_to_bitlist(b"KMAC"), s)
