# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from random import sample
from typing import Any, Dict, Tuple

import pytest
from _pytest.fixtures import SubRequest

from tvl.api.l3_api import TsL3RMemDataEraseCommand, TsL3RMemDataEraseResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model

from ..utils import UtilsRMem, as_slow


@pytest.fixture()
def prepare_data(model_configuration: Dict[str, Any], request: SubRequest):
    model_configuration.update(
        {
            "r_user_data": {
                (slot := request.param): {
                    "free": False,
                    "value": (val := UtilsRMem.get_valid_data()),
                }
            }
        }
    )
    yield slot, val


@pytest.mark.parametrize(
    "prepare_data", as_slow(UtilsRMem.VALID_INDICES, 10), indirect=True
)
def test_valid_udata_slot(
    prepare_data: Tuple[int, bytes], host: Host, model: Tropic01Model
):
    udata_slot, previous_value = prepare_data
    assert model.r_user_data[udata_slot].free is False
    assert model.r_user_data[udata_slot].value == previous_value

    command = TsL3RMemDataEraseCommand(
        udata_slot=udata_slot,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3RMemDataEraseResult)
    assert model.r_user_data[udata_slot].free is True
    assert model.r_user_data[udata_slot].value == UtilsRMem.INIT_VALUE


@pytest.mark.parametrize(
    "udata_slot", as_slow(sample(UtilsRMem.INVALID_INDICES, k=32), 10)
)
def test_invalid_udata_slot(host: Host, udata_slot: int):
    command = TsL3RMemDataEraseCommand(
        udata_slot=udata_slot,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
