# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
from binascii import unhexlify
from functools import partial
from hashlib import sha512
from pathlib import Path
from typing import List, NamedTuple

import pytest

from tvl.crypto.eddsa import eddsa_key_setup, eddsa_sign

# http://ed25519.cr.yp.to/python/sign.input
_TEST_VECTOR_FILE = Path(__file__).parent / "sign.input"


def standard_compute_r(
    s: bytes, prefix: bytes, a: bytes, m: bytes, h: bytes, n: bytes
) -> bytes:
    return sha512(prefix + m).digest()


standard_eddsa_sign = partial(eddsa_sign, compute_r_fn=standard_compute_r)


class _Vector(NamedTuple):
    secret: bytes
    public: bytes
    message: bytes
    signature: bytes


def _extract_data(filename: Path):
    data: List[_Vector] = []
    with open(filename, mode="rb") as fd:
        for line in filter(None, map(bytes.strip, fd)):
            fields = line.split(b":")
            data.append(
                _Vector(
                    unhexlify(fields[0])[:32],
                    unhexlify(fields[1]),
                    unhexlify(fields[2]),
                    unhexlify(fields[3])[:64],
                )
            )
    return data


def _get_test_vectors(filename: Path, not_slow_nb: int):
    data = _extract_data(filename)
    not_slow_indices = set(random.sample(range(len(data)), k=not_slow_nb))
    for i, vector in enumerate(data):
        if i not in not_slow_indices:
            yield pytest.param(vector, marks=pytest.mark.slow, id=str(i))
        else:
            yield pytest.param(vector, id=str(i))


@pytest.mark.xfail(reason="Verify behaviour against SPECT")
@pytest.mark.parametrize("vector", _get_test_vectors(_TEST_VECTOR_FILE, 10))
def test_standard_eddsa(vector: _Vector):
    s, prefix, a = eddsa_key_setup(vector.secret)
    assert a == vector.public

    r, s = standard_eddsa_sign(s, prefix, a, vector.message)
    assert r + s == vector.signature
