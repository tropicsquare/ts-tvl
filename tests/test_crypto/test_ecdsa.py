# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from hashlib import sha256 as _sha256

import pytest

from tvl.crypto.ecdsa import ecdsa_key_setup, ecdsa_sign_second_part

# Data from https://www.rfc-editor.org/rfc/rfc6979#appendix-A.2.5
PRIV_KEY = 0xC9AFA9D845BA75166B5C215767B1D6934E50C3DB36E89B127B8A622B120F6721
UX = 0x60FED4BA255A9D31C961EB74C6356D68C049B8923B61FA6CE669622E60F29FB6
UY = 0x7903FE1008B8BC99A41AE9E95628BC64F2F1B20C2D7E9F5177A3C294D4462299

PRIV_KEY_BYTES = PRIV_KEY.to_bytes(32, byteorder="big")
UX_BYTES = UX.to_bytes(32, byteorder="big")
UY_BYTES = UY.to_bytes(32, byteorder="big")


def sha256(data: bytes) -> bytes:
    return _sha256(data).digest()


def test_ecdsa_key_setup():
    d, _, a = ecdsa_key_setup(PRIV_KEY_BYTES)
    x, y = a[:32], a[32:]
    assert d == PRIV_KEY_BYTES
    assert x == UX_BYTES
    assert y == UY_BYTES


@pytest.mark.skip(reason="TODO")
def test_ecdsa_sign_first_part():
    pass


@pytest.mark.parametrize(
    "message, k, expected_r, expected_s",
    [
        pytest.param(
            b"sample",
            0xA6E3C57DD01ABE90086538398355DD4C3B17AA873382B0F24D6129493D8AAD60,
            0xEFD48B2AACB6A8FD1140DD9CD45E81D69D2C877B56AAF991C34D0EA84EAF3716,
            0xF7CB1C942D657C41D436C7A1B6E29F65F3E900DBB9AFF4064DC4AB2F843ACDA8,
            id="#1",
        ),
        pytest.param(
            b"test",
            0xD16B6AE827F17175E040871A1C7EC3500192C4C92677336EC2537ACAEE0008E0,
            0xF1ABB023518351CD71D881567B1EA663ED3EFCF6C5132B354F28D3B0B7D38367,
            0x019F4113742A2B14BD25926B49C649155F267E60D3814B4C0CC84250E46F0083,
            id="#2",
        ),
    ],
)
def test_ecdsa_sign_second_part(
    message: bytes, k: int, expected_r: int, expected_s: int
):
    r, s = ecdsa_sign_second_part(PRIV_KEY_BYTES, sha256(message), k)
    assert r == expected_r.to_bytes(32, byteorder="big")
    assert s == expected_s.to_bytes(32, byteorder="big")
