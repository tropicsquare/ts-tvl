import os
import random
from typing import Tuple

import pytest
from Crypto.Hash import KMAC256, cSHAKE256

from tvl.crypto.conversion import bitlist_to_bytes, ints_to_bitlist
from tvl.crypto.kmac import cshake256 as _cshake256
from tvl.crypto.kmac import kmac256 as _kmac256


def cshake256(x: bytes, l: int, n: bytes, s: bytes) -> bytes:
    return bitlist_to_bytes(
        _cshake256(
            ints_to_bitlist(x),
            l,
            ints_to_bitlist(n),
            ints_to_bitlist(s),
        )
    )


@pytest.fixture(params=range(5))
def random_values_cshake():
    x = os.urandom(random.randrange(10_000))
    l = random.randrange(10_000)
    s = os.urandom(random.randrange(10_000))
    yield x, l, s


def test_cshake256(random_values_cshake: Tuple[bytes, int, bytes]):
    x, l, s = random_values_cshake
    expected = cSHAKE256.new(data=x, custom=s).read(l)
    result = cshake256(x, l * 8, b"", s)
    assert result == expected


def kmac256(k: bytes, x: bytes, l: int, s: bytes) -> bytes:
    return bitlist_to_bytes(
        _kmac256(ints_to_bitlist(k), ints_to_bitlist(x), l, ints_to_bitlist(s))
    )


@pytest.fixture(params=range(5))
def random_values_kmac():
    k = os.urandom(32)
    x = os.urandom(random.randrange(10_000))
    l = random.randrange(8, 10_000)
    s = os.urandom(random.randrange(10_000))
    yield k, x, l, s


def test_kmac256(random_values_kmac: Tuple[bytes, bytes, int, bytes]):
    k, x, l, s = random_values_kmac
    expected = KMAC256.new(key=k, data=x, mac_len=l, custom=s).digest()
    result = kmac256(k, x, l * 8, s)
    assert result == expected
