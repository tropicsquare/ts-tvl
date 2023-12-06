import os
import random
from itertools import chain
from typing import List, Tuple

import pytest

from tvl.api.l3_api import TsL3EcdsaSignCommand, TsL3EcdsaSignResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.internal.ecc_keys import KEY_SIZE, Origins

from ..base_test import BaseTestSecureChannel
from ..utils import one_of


def _get_valid_indices() -> Tuple[List[int], List[int], List[int], List[int]]:
    indices = list(range(1, 33))
    random.shuffle(indices)
    return (
        indices[: (l := len(indices) // 4)],
        indices[l : l * 2],
        indices[l * 2 : l * 3],
        indices[l * 3 :],
    )


def _get_invalid_indices(*, k: int) -> List[int]:
    indices = [0] + list(range(33, 256))
    return random.sample(indices, k=k)


def _get_key():
    return {
        "d": os.urandom(KEY_SIZE),
        "w": os.urandom(KEY_SIZE),
        "a": os.urandom(KEY_SIZE * 2),
        "origin": one_of(Origins),
    }


def _get_msg_hash() -> bytes:
    return os.urandom(32)


OK_IDX, NO_KEY_IDX, BAD_CURVE_IDX, SIG_FAILED_IDX = _get_valid_indices()

OK_KEYS = {i: _get_key() for i in OK_IDX}


class TestEcdsaSign(BaseTestSecureChannel):
    CONFIGURATION = {
        "model": {
            "r_ecc_keys": OK_KEYS,
        }
    }

    @pytest.mark.parametrize("slot", OK_IDX)
    def test_ecdsa_signature_ok(self, host: Host, slot: int):
        command = TsL3EcdsaSignCommand(
            slot=slot,
            padding=b"",
            msg_hash=_get_msg_hash(),
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.OK
        assert isinstance(result, TsL3EcdsaSignResult)
        # TODO implement result checking against reference implementation

    @pytest.mark.parametrize(
        "slot",
        chain(
            (pytest.param(i, id=f"{i}-no_key") for i in NO_KEY_IDX),
            (pytest.param(i, id=f"{i}-curve_mismatch") for i in BAD_CURVE_IDX),
        ),
    )
    def test_no_key_and_bad_curve(self, host: Host, slot: int):
        command = TsL3EcdsaSignCommand(
            slot=slot,
            padding=b"",
            msg_hash=_get_msg_hash(),
        )
        result = host.send_command(command)

        assert result.result.value == TsL3EcdsaSignResult.ResultEnum.INVALID_KEY
        assert not isinstance(result, TsL3EcdsaSignResult)

    # TODO implement
    @pytest.mark.skip(reason="mock failed signature")
    @pytest.mark.parametrize("slot", SIG_FAILED_IDX)
    def test_signature_failed(self, host: Host, slot: int):
        command = TsL3EcdsaSignCommand(
            slot=slot,
            padding=b"",
            msg_hash=_get_msg_hash(),
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
        assert isinstance(result, TsL3EcdsaSignResult)

    @pytest.mark.parametrize("slot", _get_invalid_indices(k=10))
    def test_invalid_slot(self, host: Host, slot: int):
        command = TsL3EcdsaSignCommand(
            slot=slot,
            padding=b"",
            msg_hash=_get_msg_hash(),
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
