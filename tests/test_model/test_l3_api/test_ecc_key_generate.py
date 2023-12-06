import os
import random
from typing import List, Tuple

import pytest

from tvl.api.l3_api import TsL3EccKeyGenerateCommand, TsL3EccKeyGenerateResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.internal.ecc_keys import KEY_SIZE, Origins
from tvl.targets.model.tropic01_model import Tropic01Model

from ..base_test import BaseTestSecureChannel
from ..utils import one_of, one_outside


def _get_valid_indices() -> Tuple[List[int], List[int], List[int]]:
    indices = list(range(1, 33))
    random.shuffle(indices)
    return (
        indices[: (l := len(indices) // 3)],
        indices[l : l * 2],
        indices[l * 2 :],
    )


def _get_invalid_indices(*, k: int) -> List[int]:
    indices = [0] + list(range(33, 256))
    return random.sample(indices, k=k)


def _get_valid_data():
    if random.randint(0, 255) % 2 == 0:
        return {
            "d": os.urandom(KEY_SIZE),
            "w": os.urandom(KEY_SIZE),
            "a": os.urandom(KEY_SIZE * 2),
            "origin": one_of(Origins),
        }
    return {
        "s": os.urandom(KEY_SIZE),
        "prefix": os.urandom(KEY_SIZE),
        "a": os.urandom(KEY_SIZE),
        "origin": one_of(Origins),
    }


OK_IDX, KEY_ALREADY_EXISTS_IDX, INVALID_CURVE_IDX = _get_valid_indices()


class TestEccKeyGenerate(BaseTestSecureChannel):
    CONFIGURATION = {
        "model": {
            "r_ecc_keys": {
                **{i: _get_valid_data() for i in KEY_ALREADY_EXISTS_IDX},
            }
        }
    }

    @pytest.mark.parametrize("slot", OK_IDX)
    def test_generation_ok(self, host: Host, model: Tropic01Model, slot: int):
        assert model.r_ecc_keys.slots[slot] is None
        command = TsL3EccKeyGenerateCommand(
            slot=slot,
            curve=one_of(TsL3EccKeyGenerateCommand.CurveEnum),
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.OK
        assert isinstance(result, TsL3EccKeyGenerateResult)
        assert model.r_ecc_keys.slots[slot] is not None

    @pytest.mark.parametrize("slot", KEY_ALREADY_EXISTS_IDX)
    def test_key_already_exists(self, host: Host, model: Tropic01Model, slot: int):
        assert (before := model.r_ecc_keys.slots[slot]) is not None
        command = TsL3EccKeyGenerateCommand(
            slot=slot,
            curve=one_of(TsL3EccKeyGenerateCommand.CurveEnum),
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
        assert isinstance(result, TsL3EccKeyGenerateResult)
        assert model.r_ecc_keys.slots[slot] == before

    @pytest.mark.parametrize("slot", INVALID_CURVE_IDX)
    def test_invalid_curve(self, host: Host, model: Tropic01Model, slot: int):
        assert model.r_ecc_keys.slots[slot] is None
        command = TsL3EccKeyGenerateCommand(
            slot=slot,
            curve=one_outside(TsL3EccKeyGenerateCommand.CurveEnum),
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
        assert isinstance(result, TsL3EccKeyGenerateResult)
        assert model.r_ecc_keys.slots[slot] is None

    @pytest.mark.parametrize("slot", _get_invalid_indices(k=10))
    def test_invalid_slot(self, host: Host, model: Tropic01Model, slot: int):
        assert model.r_ecc_keys.slots[slot] is None
        command = TsL3EccKeyGenerateCommand(
            slot=slot,
            curve=one_of(TsL3EccKeyGenerateCommand.CurveEnum),
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
        assert model.r_ecc_keys.slots[slot] is None
