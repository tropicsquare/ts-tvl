# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, Tuple

import pytest
from _pytest.fixtures import SubRequest

from tvl.api.l3_api import TsL3McounterUpdateCommand, TsL3McounterUpdateResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model

from ..utils import UtilsMcounter


@pytest.fixture()
def prepare_data_ok(model_configuration: Dict[str, Any], request: SubRequest):
    model_configuration.update(
        {
            "r_mcounters": {
                (idx := request.param): {
                    "value": (val := UtilsMcounter.get_valid_data())
                }
            }
        }
    )
    yield idx, val


@pytest.mark.parametrize("prepare_data_ok", UtilsMcounter.VALID_INDICES, indirect=True)
def test_initialized(
    prepare_data_ok: Tuple[int, int], host: Host, model: Tropic01Model
):
    index, previous_value = prepare_data_ok
    assert model.r_mcounters[index].value == previous_value

    command = TsL3McounterUpdateCommand(
        mcounter_index=index,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3McounterUpdateResult)
    assert model.r_mcounters[index].value == previous_value - 1


@pytest.mark.parametrize("index", UtilsMcounter.VALID_INDICES)
def test_uninitialized(index: int, host: Host, model: Tropic01Model):
    assert model.r_mcounters[index].value == UtilsMcounter.NOTSET_VALUE

    command = TsL3McounterUpdateCommand(
        mcounter_index=index,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
    assert isinstance(result, TsL3McounterUpdateResult)
    assert model.r_mcounters[index].value == UtilsMcounter.NOTSET_VALUE


@pytest.fixture()
def index(model_configuration: Dict[str, Any], request: SubRequest):
    model_configuration.update({"r_mcounters": {(idx := request.param): {"value": 0}}})
    yield idx


@pytest.mark.parametrize("index", UtilsMcounter.VALID_INDICES, indirect=True)
def test_null(index: int, host: Host, model: Tropic01Model):
    assert model.r_mcounters[index].value == 0

    command = TsL3McounterUpdateCommand(
        mcounter_index=index,
    )
    result = host.send_command(command)

    assert result.result.value == TsL3McounterUpdateResult.ResultEnum.UPDATE_ERR
    assert isinstance(result, TsL3McounterUpdateResult)
    assert model.r_mcounters[index].value == 0


@pytest.mark.parametrize("mcounter_index", UtilsMcounter.INVALID_INDICES)
def test_invalid_index(host: Host, mcounter_index: int):
    command = TsL3McounterUpdateCommand(
        mcounter_index=mcounter_index,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
