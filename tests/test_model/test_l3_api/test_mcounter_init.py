# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
from itertools import chain, count
from typing import List, Tuple

import pytest

from tvl.api.l3_api import TsL3McounterInitCommand, TsL3McounterInitResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.internal.mcounter import MCOUNTER_MAX_VAL
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


def _get_invalid_data() -> int:
    return random.randint(MCOUNTER_MAX_VAL + 1, 2**32 - 1)


VALID_VALUE_CTR_INDICES, INVALID_VALUE_CTR_INDICES = _get_valid_indices()


VALID_VALUE_CTR = {idx: _get_valid_data() for idx in VALID_VALUE_CTR_INDICES}

INVALID_VALUE_CTR = {idx: _get_valid_data() for idx in INVALID_VALUE_CTR_INDICES}


class TestMCounterInit(BaseTestSecureChannel):
    CONFIGURATION = {
        "model": {
            "r_mcounters": {
                **{idx: {"value": value} for idx, value in VALID_VALUE_CTR.items()},
                **{idx: {"value": value} for idx, value in INVALID_VALUE_CTR.items()},
            }
        }
    }

    @pytest.mark.parametrize(
        "idx, previous_value, value, expected_result_field, expected_value",
        chain(
            (
                pytest.param(idx, value, v, L3ResultFieldEnum.OK, v, id=f"{idx}-valid")
                for (idx, value), v in zip(
                    VALID_VALUE_CTR.items(),
                    (_get_valid_data() for _ in count()),
                )
            ),
            (
                pytest.param(
                    idx,
                    value,
                    v,
                    L3ResultFieldEnum.FAIL,
                    value,
                    id=f"{idx}-invalid",
                )
                for (idx, value), v in zip(
                    INVALID_VALUE_CTR.items(),
                    (_get_invalid_data() for _ in count()),
                )
            ),
        ),
    )
    def test_valid_slot(
        self,
        host: Host,
        model: Tropic01Model,
        idx: int,
        previous_value: int,
        value: int,
        expected_result_field: int,
        expected_value: int,
    ):
        assert model.r_mcounters[idx].value == previous_value
        command = TsL3McounterInitCommand(mcounter_index=idx, mcounter_val=value)
        result = host.send_command(command)

        assert result.result.value == expected_result_field
        assert isinstance(result, TsL3McounterInitResult)
        assert model.r_mcounters[idx].value == expected_value

    @pytest.mark.parametrize("mcounter_index", _get_invalid_indices(k=10))
    def test_invalid_slot(self, host: Host, mcounter_index: int):
        command = TsL3McounterInitCommand(
            mcounter_index=mcounter_index, mcounter_val=_get_valid_data()
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
