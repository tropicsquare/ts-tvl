import random
from binascii import unhexlify as _u
from hashlib import sha512
from pathlib import Path
from typing import List, NamedTuple

import pytest

from tvl.crypto.eddsa import eddsa_key_setup, eddsa_sign, eddsa_verify, ts_compute_r

# http://ed25519.cr.yp.to/python/sign.input
_TEST_VECTOR_FILE = Path(__file__).parent / "sign.input"


def _b(__i: int, /) -> bytes:
    return __i.to_bytes(32, "little")


class _StandardVector(NamedTuple):
    secret: bytes
    public: bytes
    message: bytes
    signature: bytes


def _extract_data(filename: Path):
    data: List[_StandardVector] = []
    with open(filename, mode="rb") as fd:
        for line in filter(None, map(bytes.strip, fd)):
            fields = line.split(b":")
            data.append(
                _StandardVector(
                    _u(fields[0])[:32],
                    _u(fields[1]),
                    _u(fields[2]),
                    _u(fields[3])[:64],
                )
            )
    return data


def _get_standard_test_vectors(filename: Path, not_slow_nb: int):
    data = _extract_data(filename)
    not_slow_indices = set(random.sample(range(len(data)), k=not_slow_nb))
    for i, vector in enumerate(data):
        if i not in not_slow_indices:
            yield pytest.param(vector, marks=pytest.mark.slow, id=str(i))
        else:
            yield pytest.param(vector, id=str(i))


def standard_compute_r(
    s: bytes, prefix: bytes, a: bytes, m: bytes, h: bytes, n: bytes
) -> int:
    return int.from_bytes(sha512(prefix + m).digest(), "little")


@pytest.mark.parametrize("vector", _get_standard_test_vectors(_TEST_VECTOR_FILE, 10))
def test_standard_eddsa(vector: _StandardVector):
    s, prefix, a = eddsa_key_setup(vector.secret)
    assert a == vector.public

    r, s = eddsa_sign(s, prefix, a, vector.message, compute_r_fn=standard_compute_r)
    assert r + s == vector.signature


class _TropicVector(NamedTuple):
    k: bytes
    s: bytes
    prefix: bytes
    a: bytes
    msg: bytes
    sch: bytes
    scn: bytes
    r: int
    signature: bytes


_VECTORS_TROPIC = [
    _TropicVector(
        _u(b"581b36299845b864b5eeaf9ad506f53158b190ab8f083f3ae3d907f11dea297c"),
        _b(0xBE596FD767D3D700CF05A234C72BE9DEAC339398280A9793861A1C21DF55A45),
        _b(0x347C5C7948ED1467009FCEA9EA1E9AF6E54E1B853EE53A2064F506B78537545),
        _u(b"290d5980490861b5a2b44458f1511f8bcd6691c3389ef2c7c701b7d6a5c524a2"),
        _u(b"8efc2e6dc1bd4d5936619820d5bfb11d"),
        _u(b"e7977bef7a7441a4a76ca38d8dbc857d2e187beeccf4374e5e3a40d711648de5"),
        _u(b"f0f16636"),
        0x64635D4015F8BB9529398C352AFF581D17D77156257EBDC329ABFD98D0E87B8,
        _u(
            b"3910ce719b9f05eb6086a0a2dd3814dc58b6277a41331c55908b9c6acb5df06a5991dd0d59229b80da39f44188cbc5ef87bbf86c18dfea0a6dceb8aa0325a90d"
        ),
    ),
    _TropicVector(
        _u(b"687b3b9410e3cc3a5aeeb2752da8e31eb3072f115d638612c9746d81e13e1831"),
        _b(0x61B67D2924E9194FBD7BA4732F87EEF2DAFB52215EB34E39181F607227D86F7),
        _b(0x1E07C45204DFD39978B66F346797E70B822C31B377EA9CD39680BD501D5E9006),
        _u(b"ea80aa098a1486722ef4d9cc37cc7819738a49726a3f344d2ab2acd622681aa7"),
        _u(b"b6d8"),
        _u(b"11a19e1ecd0f6b4b25958acb0bdf3ae0cba4359a66cfbebf69154f8944597b53"),
        _u(b"546e9a21"),
        0xDA584BCAEF7AE3B196C045EDA6E37F3F702589ED348183061610D17D55E0D6C,
        _u(
            b"bd30e92b0cf9dc9100b9124cb75357404632d0704477db9e4c596fd80e46a247b4a0641458f01aa4a075f9680f988b50fd2554b495f71b60f833adde63e38b0f"
        ),
    ),
    _TropicVector(
        _u(b"2f0d891849ebaad8b735e847ea28b81f97a6dfe08388741775c48bd846fca1c1"),
        _b(0xF6F6BF11C648DC25B198CB03393148653006D6A20FE10D093F5277F23D2A47C),
        _b(0x8027E9ABBEBE131296134BF62893D5D59B5A74A5F191977B08F919DD27695B4E),
        _u(b"5ae16898c02267ae157ca0b7cde90362c514ec9c76742765f7e2e1436adaccd3"),
        _u(b"4fcd06cea7aebf4faae1436e713bcf834dd4"),
        _u(b"26f81f859a52df4be4f2f5660e0096ef9075ca5f12fc08c9d005e03f0a04facd"),
        _u(b"8976344b"),
        0x81B0B30B4F13465C16F39E5E0E7502494E02535C4EAFC1551494228880975A8,
        _u(
            b"3b85f7cf672bbfe936a19af88627c46fa6e81063add7d6e06c44aa088b90232720f59533796fc0ad40b16c0251913cbeefdd6552f5050cd7fec1414ea68c2908"
        ),
    ),
]


@pytest.mark.parametrize("vector", _VECTORS_TROPIC)
def test_tropic_key_setup(vector: _TropicVector):
    s, prefix, a = eddsa_key_setup(vector.k)
    assert s == vector.s
    assert prefix == vector.prefix
    assert a == vector.a


@pytest.mark.parametrize("vector", _VECTORS_TROPIC)
def test_tropic_compute_r(vector: _TropicVector):
    r = ts_compute_r(
        vector.s, vector.prefix, vector.a, vector.msg, vector.sch, vector.scn
    )
    assert r == vector.r


@pytest.mark.parametrize("vector", _VECTORS_TROPIC)
def test_tropic_eddsa(vector: _TropicVector):
    r, s = eddsa_sign(
        vector.s, vector.prefix, vector.a, vector.msg, vector.sch, vector.scn
    )
    assert r + s == vector.signature

@pytest.mark.parametrize("vector", _VECTORS_TROPIC)
def test_tropic_eddsa_verify(vector: _TropicVector):
    r, s = eddsa_sign(
        vector.s, vector.prefix, vector.a, vector.msg, vector.sch, vector.scn
    )
    assert eddsa_verify(vector.msg, r, s, vector.a) is True