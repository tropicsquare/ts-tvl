# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
from typing import List, Tuple

import pytest

from tvl.api.l3_api import TsL3McounterGetCommand, TsL3McounterGetResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.internal.mcounter import MCOUNTER_MAX_VAL, NOTSET_VALUE
from tvl.targets.model.tropic01_model import Tropic01Model

from ..base_test import BaseTestSecureChannel


def _get_valid_indices() -> Tuple[List[int], List[int]]:
    indices = list(range(1, 17))
    random.shuffle(indices)
    return indices[: (hl := len(indices) // 2)], indices[hl:]


def _get_invalid_indices(*, k: int) -> List[int]:
    indices = [0] + list(range(17, 256))
    return random.sample(indices, k=k)


def _get_valid_data() -> int:
    return random.randint(0, MCOUNTER_MAX_VAL)


INITIALIZED_CTR_INDICES, NOTSET_CTR_INDICES = _get_valid_indices()

R_MCOUNTERS_CFG = {idx: _get_valid_data() for idx in INITIALIZED_CTR_INDICES}


class TestMCounterGet(BaseTestSecureChannel):
    CONFIGURATION = {
        "model": {
            "r_mcounters": {
                idx: {"value": value} for idx, value in R_MCOUNTERS_CFG.items()
            }
        }
    }

    @pytest.mark.parametrize(
        "mcounter_index, value",
        (
            pytest.param(idx, value, id=str(idx))
            for idx, value in R_MCOUNTERS_CFG.items()
        ),
    )
    def test_get_initialized_counter(
        self, host: Host, model: Tropic01Model, mcounter_index: int, value: int
    ):
        assert model.r_mcounters[mcounter_index].value == value

        command = TsL3McounterGetCommand(
            mcounter_index=mcounter_index,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.OK
        assert isinstance(result, TsL3McounterGetResult)
        assert result.mcounter_val.value == value

    @pytest.mark.parametrize("mcounter_index", NOTSET_CTR_INDICES)
    def test_get_notset_counter(
        self, host: Host, model: Tropic01Model, mcounter_index: int
    ):
        assert model.r_mcounters[mcounter_index].value == NOTSET_VALUE

        command = TsL3McounterGetCommand(
            mcounter_index=mcounter_index,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
        assert model.r_mcounters[mcounter_index].value == NOTSET_VALUE

    @pytest.mark.parametrize("mcounter_index", _get_invalid_indices(k=10))
    def test_invalid_slot(self, host: Host, model: Tropic01Model, mcounter_index: int):
        command = TsL3McounterGetCommand(
            mcounter_index=mcounter_index,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
