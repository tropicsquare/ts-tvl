# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
import random
from itertools import chain
from typing import List, Tuple

import pytest

from tvl.api.l3_api import TsL3EddsaSignCommand, TsL3EddsaSignResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.internal.ecc_keys import KEY_SIZE, Origins

from ..base_test import BaseTestSecureChannel
from ..utils import one_of


def _get_valid_indices() -> Tuple[List[int], List[int], List[int]]:
    indices = list(range(1, 33))
    random.shuffle(indices)
    return (
        indices[: (l := len(indices) // 4)],
        indices[l : l * 2],
        indices[l * 2 :],
    )


def _get_invalid_indices(*, k: int) -> List[int]:
    indices = [0] + list(range(33, 256))
    return random.sample(indices, k=k)


def _get_key():
    return {
        "s": os.urandom(KEY_SIZE),
        "prefix": os.urandom(KEY_SIZE),
        "a": os.urandom(KEY_SIZE),
        "origin": one_of(Origins),
    }


def _get_msg() -> bytes:
    return os.urandom(random.randint(1, 4096))


OK_IDX, NO_KEY_IDX, BAD_CURVE_IDX = _get_valid_indices()

OK_KEYS = {i: _get_key() for i in OK_IDX}


class TestEddsaSign(BaseTestSecureChannel):
    CONFIGURATION = {
        "model": {
            "r_ecc_keys": OK_KEYS,
        }
    }

    @pytest.mark.parametrize("slot", OK_IDX)
    def test_ecdsa_signature_ok(self, host: Host, slot: int):
        command = TsL3EddsaSignCommand(
            slot=slot,
            padding=b"",
            msg=_get_msg(),
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.OK
        assert isinstance(result, TsL3EddsaSignResult)
        # TODO implement result checking against reference implementation

    @pytest.mark.parametrize(
        "slot",
        chain(
            (pytest.param(i, id=f"{i}-no_key") for i in NO_KEY_IDX),
            (pytest.param(i, id=f"{i}-curve_mismatch") for i in BAD_CURVE_IDX),
        ),
    )
    def test_no_key_and_bad_curve(self, host: Host, slot: int):
        command = TsL3EddsaSignCommand(
            slot=slot,
            padding=b"",
            msg=_get_msg(),
        )
        result = host.send_command(command)

        assert result.result.value == TsL3EddsaSignResult.ResultEnum.INVALID_KEY
        assert not isinstance(result, TsL3EddsaSignResult)

    @pytest.mark.parametrize("slot", _get_invalid_indices(k=10))
    def test_invalid_slot(self, host: Host, slot: int):
        command = TsL3EddsaSignCommand(
            slot=slot,
            padding=b"",
            msg=_get_msg(),
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
