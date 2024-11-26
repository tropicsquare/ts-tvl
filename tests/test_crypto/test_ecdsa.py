# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from binascii import unhexlify as _u
from hashlib import sha256 as _sha256
from typing import NamedTuple

import pytest

from tvl.crypto.ecdsa import (
    ecdsa_key_setup,
    ecdsa_sign,
    ecdsa_sign_first_part,
    ecdsa_sign_second_part,
)


def _b(__i: int, /) -> bytes:
    return __i.to_bytes(32, byteorder="big")


# Data from https://www.rfc-editor.org/rfc/rfc6979#appendix-A.2.5
PRIV_KEY = _b(0xC9AFA9D845BA75166B5C215767B1D6934E50C3DB36E89B127B8A622B120F6721)
UX = _b(0x60FED4BA255A9D31C961EB74C6356D68C049B8923B61FA6CE669622E60F29FB6)
UY = _b(0x7903FE1008B8BC99A41AE9E95628BC64F2F1B20C2D7E9F5177A3C294D4462299)


def sha256(data: bytes) -> bytes:
    return _sha256(data).digest()


def test_standard_ecdsa_key_setup():
    d, _, a = ecdsa_key_setup(k := PRIV_KEY)
    assert d == k
    assert a == UX + UY


@pytest.mark.parametrize(
    "message, k, expected_r, expected_s",
    [
        pytest.param(
            b"sample",
            0xA6E3C57DD01ABE90086538398355DD4C3B17AA873382B0F24D6129493D8AAD60,
            0xEFD48B2AACB6A8FD1140DD9CD45E81D69D2C877B56AAF991C34D0EA84EAF3716,
            0xF7CB1C942D657C41D436C7A1B6E29F65F3E900DBB9AFF4064DC4AB2F843ACDA8,
            id="standard #1",
        ),
        pytest.param(
            b"test",
            0xD16B6AE827F17175E040871A1C7EC3500192C4C92677336EC2537ACAEE0008E0,
            0xF1ABB023518351CD71D881567B1EA663ED3EFCF6C5132B354F28D3B0B7D38367,
            0x019F4113742A2B14BD25926B49C649155F267E60D3814B4C0CC84250E46F0083,
            id="standard #2",
        ),
    ],
)
def test_standard_ecdsa_sign_second_part(
    message: bytes, k: int, expected_r: int, expected_s: int
):
    r, s = ecdsa_sign_second_part(PRIV_KEY, sha256(message), k)
    assert r == _b(expected_r)
    assert s == _b(expected_s)


class _TropicVector(NamedTuple):
    k: bytes
    d: bytes
    w: bytes
    ax: bytes
    ay: bytes
    z: bytes
    sch: bytes
    scn: bytes
    nonce: int
    r: bytes
    s: bytes
    signature: bytes


_TROPIC_VECTORS = [
    _TropicVector(
        _u(b"0445f93cfd6e103065e4f9cd1fd27bbedfbbfa00e91ce5467b822dbf0311ab99"),
        _b(0x445F93CFD6E103065E4F9CD1FD27BBEDFBBFA00E91CE5467B822DBF0311AB99),
        _b(0x16975261397E082796C536588B35F82801E5F1FAAE64AC624FB6D2027FA2D3FB),
        _b(0x94DBFF90877E2D74301BEE81C622CC134488BD65B7003CAFB5BF0FC324690048),
        _b(0x6C6FF4186ADFD13170B1BE15C2BE8240E19B6AC4D492DD83C8FFC958A94B775B),
        _u(b"7bb95ec1a1225601c341935b29c67912da9039f8717f810145b81b4332845cb6"),
        _u(b"c2f3445d478687adecdd705424b477e1f37edf6943a05abc2fab6bbe006002a7"),
        _u(b"4f199ffd"),
        0xCABAB381A05DEC5CCD2611F4785B9308C4745E085A00D3AB8D2260AAE78E5E28,
        _b(0xB6AEDA72AD8C6FC66246537D9529568B08366782F62206B206BB208E97E7CD1C),
        _b(0x9805DA6CF241FBF086A667DA147E110AF75F342615776C26C046C60EA55D7FD3),
        _u(
            b"b6aeda72ad8c6fc66246537d9529568b08366782f62206b206bb208e97e7cd1c9805da6cf241fbf086a667da147e110af75f342615776c26c046c60ea55d7fd3"
        ),
    ),
    _TropicVector(
        _u(b"040dd46b30572d9a94b84d198d9f4ad1b964cf08be2e2a84daa157a098f93f5b"),
        _b(0x40DD46B30572D9A94B84D198D9F4AD1B964CF08BE2E2A84DAA157A098F93F5B),
        _b(0x2F70F164919490C73458A237058788F581D47323411E0BCEA6243F59E4D2E439),
        _b(0x32CBC1841C8BD659E3C8FB214997E4FAE246997AB2F620602FDA3EC509B1D905),
        _b(0xC1BF227B78A34CB3B273C7A49723365F45DDBCC80BFC999FAA4B32E5FC31169A),
        _u(b"de0053a05219396e4d7274f90d98511aad0a1dc6876a6a83a1301305f4e9db5b"),
        _u(b"fe7dfcb81abb9e5468914c26286da13cf7d0ad39cf01916b1504096d7e6ec251"),
        _u(b"f9a9c78a"),
        0xFD0485106DE094BD568B2BEDFF947DEBFF71416CEBE38376F2488F69DAF9DF16,
        _b(0xB2084F99DC76ED4B1D5AC4EA35A9B56EF826E1588B8CCD2B49B67A2806BED98),
        _b(0xD22C3D902ABD35C1B202072336340F0F22A563811604C9382AA46A840DD95863),
        _u(
            b"0b2084f99dc76ed4b1d5ac4ea35a9b56ef826e1588b8ccd2b49b67a2806bed98d22c3d902abd35c1b202072336340f0f22a563811604c9382aa46a840dd95863"
        ),
    ),
    _TropicVector(
        _u(b"5b90403fc836ca7c297da24ff8e5daeed2e86a77de72073cd2e33133d909fa0f"),
        _b(0x5B90403FC836CA7C297DA24FF8E5DAEED2E86A77DE72073CD2E33133D909FA0F),
        _b(0xF91DCCD1541A7339A869C3771474DA6532286C74A0C197F731FB70C747B6949),
        _b(0x722A64DBF518F03EEE720880E9676D59DC5486402F4CC61642A7532FC7751F30),
        _b(0x3713BBCBB5849B2CC2939D370435AA4A1236D12C15E05D923066F9DCDB7077D7),
        _u(b"36cd3490483d9b5f15f54f1c9a2de5ffe66eaf622676fd6ebe73fd500ca95ccc"),
        _u(b"a0c1da7afadbc908955d52b7c0b4b68d18b02772ffdf4d56b453a25ec040876b"),
        _u(b"a1657686"),
        0xD6322E28D2C2CDBF369D5CF4E2BFB414CB994E07D5F22B2E10D849E58DFCB59B,
        _b(0x3F9E5463F596A60C9461EC87175B4FD91E9712E37E4489F068E7ACB4686D2461),
        _b(0x709017B37BFEF8520702C58B35836A87D81F7DEC9A09CDA4146B5231D7D29B4D),
        _u(
            b"3f9e5463f596a60c9461ec87175b4fd91e9712e37e4489f068e7acb4686d2461709017b37bfef8520702c58b35836a87d81f7dec9a09cda4146b5231d7d29b4d"
        ),
    ),
]


@pytest.mark.parametrize("vector", _TROPIC_VECTORS)
def test_key_setup(vector: _TropicVector):
    d, w, a = ecdsa_key_setup(vector.k)
    assert d == vector.d
    assert w == vector.w
    assert a == vector.ax + vector.ay


@pytest.mark.parametrize("vector", _TROPIC_VECTORS)
def test_sign(vector: _TropicVector):
    r, s = ecdsa_sign(vector.d, vector.w, vector.z, vector.sch, vector.scn)
    assert r + s == vector.signature


@pytest.mark.parametrize("vector", _TROPIC_VECTORS)
def test_sign_first_part(vector: _TropicVector):
    d, z, k_int = ecdsa_sign_first_part(
        vector.d, vector.w, vector.z, vector.sch, vector.scn
    )
    assert d == vector.d
    assert z == vector.z
    assert k_int == vector.nonce


@pytest.mark.parametrize("vector", _TROPIC_VECTORS)
def test_sign_second_part(vector: _TropicVector):
    r, s = ecdsa_sign_second_part(vector.d, vector.z, vector.nonce)
    assert r + s == vector.signature
