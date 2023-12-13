# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
from itertools import chain
from typing import List, Tuple

import pytest

from tvl.api.l3_api import TsL3McounterUpdateCommand, TsL3McounterUpdateResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.internal.mcounter import MCOUNTER_MAX_VAL, NOTSET_VALUE
from tvl.targets.model.tropic01_model import Tropic01Model

from ..base_test import BaseTestSecureChannel


def _get_valid_indices() -> Tuple[List[int], List[int], List[int]]:
    indices = list(range(1, 17))
    random.shuffle(indices)
    return (
        indices[: (hl := len(indices) // 3)],
        indices[hl : hl * 2],
        indices[hl * 2 :],
    )


def _get_invalid_indices(*, k: int) -> List[int]:
    indices = [0] + list(range(17, 256))
    return random.sample(indices, k=k)


def _get_valid_data() -> int:
    return random.randint(0, MCOUNTER_MAX_VAL)


INIT_CTR_INDICES, NOTSET_CTR_INDICES, NULL_CTR_INDICES = _get_valid_indices()

INIT_CTR = {idx: _get_valid_data() for idx in INIT_CTR_INDICES}

NULL_CTR = {idx: 0 for idx in NULL_CTR_INDICES}


class TestMCounterUpdate(BaseTestSecureChannel):
    CONFIGURATION = {
        "model": {
            "r_mcounters": {
                **{idx: {"value": value} for idx, value in INIT_CTR.items()},
                **{idx: {"value": value} for idx, value in NULL_CTR.items()},
            }
        }
    }

    @pytest.mark.parametrize(
        "idx, previous_value, expected_result_field, expected_value",
        chain(
            (
                pytest.param(
                    idx,
                    value,
                    L3ResultFieldEnum.OK,
                    value - 1,
                    id=f"{idx}-initialized",
                )
                for idx, value in INIT_CTR.items()
            ),
            (
                pytest.param(
                    idx,
                    value,
                    TsL3McounterUpdateResult.ResultEnum.UPDATE_ERR,
                    value,
                    id=f"{idx}-null",
                )
                for idx, value in NULL_CTR.items()
            ),
            (
                pytest.param(
                    idx,
                    NOTSET_VALUE,
                    L3ResultFieldEnum.FAIL,
                    NOTSET_VALUE,
                    id=f"{idx}-uninitialized",
                )
                for idx in NOTSET_CTR_INDICES
            ),
        ),
    )
    def test_valid_slot(
        self,
        host: Host,
        model: Tropic01Model,
        idx: int,
        previous_value: int,
        expected_result_field: int,
        expected_value: int,
    ):
        assert model.r_mcounters[idx].value == previous_value

        command = TsL3McounterUpdateCommand(
            mcounter_index=idx,
        )
        result = host.send_command(command)

        assert result.result.value == expected_result_field
        assert isinstance(result, TsL3McounterUpdateResult)
        assert model.r_mcounters[idx].value == expected_value

    @pytest.mark.parametrize("mcounter_index", _get_invalid_indices(k=10))
    def test_invalid_slot(self, host: Host, mcounter_index: int):
        command = TsL3McounterUpdateCommand(
            mcounter_index=mcounter_index,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
