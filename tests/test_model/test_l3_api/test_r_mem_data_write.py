# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
import random
from itertools import chain, count
from typing import Iterator, List, Tuple

import pytest

from tvl.api.l3_api import TsL3RMemDataWriteCommand, TsL3RMemDataWriteResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.internal.user_data_partition import SLOT_SIZE_BYTES
from tvl.targets.model.tropic01_model import Tropic01Model

from ..base_test import BaseTestSecureChannel


def _get_valid_indices() -> Tuple[List[int], List[int]]:
    indices = list(range(1, 513))
    random.shuffle(indices)
    return indices[: (hl := len(indices) // 2)], indices[hl:]


def _get_invalid_indices(*, k: int) -> Iterator[int]:
    yield 0
    for _ in range(k - 1):
        yield random.randint(513, 2**16 - 1)


def _get_data() -> bytes:
    return os.urandom(random.randint(1, SLOT_SIZE_BYTES))


FREE_SLOT_INDICES, WRITTEN_SLOT_INDICES = _get_valid_indices()

FREE_SLOTS = {idx: _get_data() for idx in FREE_SLOT_INDICES}
WRITTEN_SLOTS = {idx: _get_data() for idx in WRITTEN_SLOT_INDICES}


class TestRMemDataWrite(BaseTestSecureChannel):
    CONFIGURATION = {
        "model": {
            "r_user_data": {
                **{
                    idx: {"free": True, "value": value}
                    for idx, value in FREE_SLOTS.items()
                },
                **{
                    idx: {"free": False, "value": value}
                    for idx, value in WRITTEN_SLOTS.items()
                },
            }
        }
    }

    @pytest.mark.parametrize(
        "udata_slot, previous_state, previous_data, data, expected_result_field, expected_data",
        chain(
            (
                pytest.param(
                    idx,
                    True,
                    value,
                    v,
                    L3ResultFieldEnum.OK,
                    v,
                    id=f"{idx}-free",
                )
                for (idx, value), v in zip(
                    FREE_SLOTS.items(), (_get_data() for _ in count())
                )
            ),
            (
                pytest.param(
                    idx,
                    False,
                    value,
                    v,
                    TsL3RMemDataWriteResult.ResultEnum.WRITE_FAIL,
                    value,
                    id=f"{idx}-written",
                )
                for (idx, value), v in zip(
                    WRITTEN_SLOTS.items(), (_get_data() for _ in count())
                )
            ),
        ),
    )
    def test_valid_udata_slot(
        self,
        host: Host,
        model: Tropic01Model,
        udata_slot: int,
        previous_state: bool,
        previous_data: bytes,
        data: bytes,
        expected_result_field: int,
        expected_data: bytes,
    ):
        assert model.r_user_data[udata_slot].free == previous_state
        assert model.r_user_data[udata_slot].value == previous_data
        command = TsL3RMemDataWriteCommand(
            udata_slot=udata_slot,
            data=data,
        )
        result = host.send_command(command)

        assert result.result.value == expected_result_field
        assert model.r_user_data[udata_slot].free is False
        assert model.r_user_data[udata_slot].value == expected_data

    @pytest.mark.parametrize("udata_slot", _get_invalid_indices(k=10))
    def test_invalid_udata_slot(self, host: Host, udata_slot: int):
        command = TsL3RMemDataWriteCommand(
            udata_slot=udata_slot,
            data=_get_data(),
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
