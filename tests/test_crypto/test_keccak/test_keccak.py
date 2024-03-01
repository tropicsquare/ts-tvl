# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
import random
from binascii import unhexlify
from pathlib import Path
from typing import Callable, List, NamedTuple, Tuple

import pytest
from Crypto.Hash import SHAKE256

from tvl.crypto.conversion import bit, bitlist_to_bytes, ints_to_bitlist
from tvl.crypto.keccak import State, keccak_c, keccak_f
from tvl.crypto.keccak import shake256 as _shake256

_CUR_DIR = Path(__file__).parent


class _Data(NamedTuple):
    data_in: bytes
    expected_data_out: bytes


def _extract_data(filename: Path):
    def _fmt_bytes(s: bytes) -> bytes:
        return unhexlify(s.replace(b" ", b""))

    with open(filename, mode="rb") as fd:
        it = filter(None, map(bytes.strip, fd))

        data_in, expected_data_out = b"", b""
        for line in it:
            if line == b"Input of permutation:":
                data_in = _fmt_bytes(next(it))
            elif line == b"State after permutation:":
                expected_data_out = _fmt_bytes(next(it))
                yield _Data(data_in, expected_data_out)
                data_in, expected_data_out = b"", b""


def _get_test_vectors(*__args: Tuple[int, int, str, str]):
    for bitrate, width, filename, id_ in __args:
        for i, vector in enumerate(_extract_data(_CUR_DIR / filename)):
            yield pytest.param(bitrate, width, vector, id=f"{id_}-{i}")


# https://github.com/XKCP/XKCP/blob/master/tests/TestVectors/
@pytest.mark.parametrize(
    "bitrate, width, data",
    _get_test_vectors(
        (72, 200, "KeccakF-200-IntermediateValues.txt", "xkcp_200"),
        (144, 400, "KeccakF-400-IntermediateValues.txt", "xkcp_400"),
        (608, 800, "KeccakF-800-IntermediateValues.txt", "xkcp_800"),
        (576, 1600, "KeccakF-1600-IntermediateValues.txt", "xkcp_1600"),
    ),
)
def test_permutation(bitrate: int, width: int, data: _Data):
    data_in, expected_data_out = data
    state = State(width, bitrate)
    state.set_array(data_in)
    keccak_f(state.b)(state.array)
    assert bytes(state.squeeze()) == expected_data_out


@pytest.mark.parametrize(
    "sponge, data_in, expected_data_out",
    [
        pytest.param(
            keccak_c(576),
            "cc",
            "56B97029B479FF5DD15F17D12983E3B835BB0531D9B8D49B103B025CA53F991741298E961D1FAD00FC365C7761BFB278AE473980D612C1629E075A3FDBAE7F82B0F0AF54DF187F358852E19EA4347CF5CEEA676A1DCE3A47447E237FD74204F9A4B7F7C9CC7CC8B865B1D554E2F5F4A8EE17DBDDE7267894558A20972C9EB6CF5F62CE9151437718ED4AFF08FA76D803806E6CE47D229AAE839369E31888B26429E27BC3756021CB51498BCF2527D4BB04838BC1CEED9985A2A66FF8CB8C2D58B7099304E7F9622C583B093024A5FCDE2BE781474C159DF24D77D328C298F5766A8A0DBF7AE790A509CCF59E0CACD0ABF21492E0095A87ECDB55990093917AAA96D7F68B7B859B8094AEC0DDB6FB352A6CC1F007FA988ED764F5D6F21F9D8ADE9CE7ACA4DE6570DA39D9ACCEB46D2582FA4C4231DE0B736FB341041D24CFAE6C0761F43A2CF7383F38742579218AFCAB53D2E6816640DE05644D877558E965B1A28406999F31CCC43AC0B02BC5448B66AD3B6F8DE04C0E25845C8671B6F0594909A057F17FD06031707C8B4599889C994A35C193DBF84A7A0919CD054F67CEB7965F420D02DA3477EFC8B55413C241ADCF71CB10FE7E3E720B8C1736837B06E4B27461B71C6CAC892437530BBFE05CF426272F80F11709B9DB964F5DEDAB9E757C2F7A972B6A4C2443B03AD787AB1E243660BCED739157A434800696841ACEA4",
            id="keccak-576",
        ),
        pytest.param(
            keccak_c(1024),
            "cc",
            "8630c13cbd066ea74bbe7fe468fec1dee10edc1254fb4c1b7c5fd69b646e44160b8ce01d05a0908ca790dfb080f4b513bc3b6225ece7a810371441a5ac666eb9",
            id="keccak-1024",
        ),
        pytest.param(
            keccak_c(448),
            "41fb",
            "615ba367afdc35aac397bc7eb5d58d106a734b24986d5d978fefd62c",
            id="keccak-448-short",
        ),
        pytest.param(
            keccak_c(448),
            "023D91AC532601C7CA3942D62827566D9268BB4276FCAA1AE927693A6961652676DBA09219A01B3D5ADFA12547A946E78F3C5C62DD880B02D2EEEB4B96636529C6B01120B23EFC49CCFB36B8497CD19767B53710A636683BC5E0E5C9534CFC004691E87D1BEE39B86B953572927BD668620EAB87836D9F3F8F28ACE41150776C0BC6657178EBF297FE1F7214EDD9F215FFB491B681B06AC2032D35E6FDF832A8B06056DA70D77F1E9B4D26AE712D8523C86F79250718405F91B0A87C725F2D3F52088965F887D8CF87206DFDE422386E58EDDA34DDE2783B3049B86917B4628027A05D4D1F429D2B49C4B1C898DDDCB82F343E145596DE11A54182F39F4718ECAE8F506BD9739F5CD5D5686D7FEFC834514CD1B2C91C33B381B45E2E5335D7A8720A8F17AFC8C2CB2BD88B14AA2DCA099B00AA575D0A0CCF099CDEC4870FB710D2680E60C48BFC291FF0CEF2EEBF9B36902E9FBA8C889BF6B4B9F5CE53A19B0D9399CD19D61BD08C0C2EC25E099959848E6A550CA7137B63F43138D7B651",
            "230620d710cf3ab835059e1aa170735db17cae74b345765ff02e8d89",
            id="keccak-448-long",
        ),
    ],
)
def test_preset(
    sponge: Callable[[List[bit], int], List[bit]],
    data_in: str,
    expected_data_out: str,
):
    res = bitlist_to_bytes(
        sponge(
            ints_to_bitlist(unhexlify(data_in)),
            len(expected_data_out) // 2 * 8,
        )
    )
    assert res == unhexlify(expected_data_out)


def shake256(m: bytes, d: int) -> bytes:
    return bitlist_to_bytes(_shake256(ints_to_bitlist(m), d))


@pytest.fixture(params=range(5))
def random_values_shake():
    m = os.urandom(random.randrange(10_000))
    d = random.randrange(10_000)
    yield m, d


def test_shake256(random_values_shake: Tuple[bytes, int]):
    m, d = random_values_shake
    expected = SHAKE256.new(data=m).read(d)
    result = shake256(m, d * 8)
    assert result == expected
