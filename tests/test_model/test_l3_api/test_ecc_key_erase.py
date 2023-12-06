import os
import random
from typing import List, Tuple

import pytest

from tvl.api.l3_api import TsL3EccKeyEraseCommand, TsL3EccKeyEraseResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.internal.ecc_keys import KEY_SIZE, Origins
from tvl.targets.model.tropic01_model import Tropic01Model

from ..base_test import BaseTestSecureChannel
from ..utils import one_of


def _get_valid_indices() -> Tuple[List[int], List[int]]:
    indices = list(range(1, 33))
    random.shuffle(indices)
    return indices[: (hl := len(indices) // 2)], indices[hl:]


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


OK_IDX, NO_KEY_IDX = _get_valid_indices()


class TestEccKeyRead(BaseTestSecureChannel):
    CONFIGURATION = {
        "model": {
            "r_ecc_keys": {
                **{i: _get_valid_data() for i in OK_IDX},
            }
        }
    }

    @pytest.mark.parametrize("slot", OK_IDX)
    def test_erasing_ok(self, host: Host, model: Tropic01Model, slot: int):
        assert model.r_ecc_keys.slots[slot] is not None
        command = TsL3EccKeyEraseCommand(
            slot=slot,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.OK
        assert isinstance(result, TsL3EccKeyEraseResult)
        assert model.r_ecc_keys.slots[slot] is None

    @pytest.mark.parametrize("slot", NO_KEY_IDX)
    def test_no_key(self, host: Host, model: Tropic01Model, slot: int):
        assert model.r_ecc_keys.slots[slot] is None
        command = TsL3EccKeyEraseCommand(
            slot=slot,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
        assert isinstance(result, TsL3EccKeyEraseResult)
        assert model.r_ecc_keys.slots[slot] is None

    @pytest.mark.parametrize("slot", _get_invalid_indices(k=10))
    def test_invalid_slot(self, host: Host, model: Tropic01Model, slot: int):
        assert model.r_ecc_keys.slots[slot] is None
        command = TsL3EccKeyEraseCommand(
            slot=slot,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
        assert model.r_ecc_keys.slots[slot] is None
