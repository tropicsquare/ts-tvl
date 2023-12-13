# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
import random
from typing import Iterator

import pytest

from tvl.api.l3_api import TsL3RMemDataReadCommand, TsL3RMemDataReadResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.internal.user_data_partition import SLOT_SIZE_BYTES
from tvl.targets.model.tropic01_model import Tropic01Model

from ..base_test import BaseTestSecureChannel


def _get_valid_indices() -> range:
    return range(1, 513)


def _get_invalid_indices(*, k: int) -> Iterator[int]:
    yield 0
    for _ in range(k - 1):
        yield random.randint(513, 2**16 - 1)


SLOT_CONFIG = {
    i: os.urandom(random.randint(1, SLOT_SIZE_BYTES)) for i in _get_valid_indices()
}


class TestRMemDataRead(BaseTestSecureChannel):
    CONFIGURATION = {
        "model": {
            "r_user_data": {
                udata_slot: {"free": False, "value": value}
                for udata_slot, value in SLOT_CONFIG.items()
            }
        }
    }

    @pytest.mark.parametrize(
        "udata_slot, value",
        (pytest.param(i, value, id=str(i)) for i, value in SLOT_CONFIG.items()),
    )
    def test_valid_udata_slot(
        self, host: Host, model: Tropic01Model, udata_slot: int, value: bytes
    ):
        assert model.r_user_data[udata_slot].free is False
        assert model.r_user_data[udata_slot].value == value

        command = TsL3RMemDataReadCommand(
            udata_slot=udata_slot,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.OK
        assert isinstance(result, TsL3RMemDataReadResult)
        assert result.data.to_bytes() == value

    @pytest.mark.parametrize("udata_slot", _get_invalid_indices(k=10))
    def test_invalid_udata_slot(self, host: Host, udata_slot: int):
        command = TsL3RMemDataReadCommand(
            udata_slot=udata_slot,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
