# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, Tuple

import pytest
from _pytest.fixtures import SubRequest

from tvl.api.l3_api import TsL3McounterGetCommand, TsL3McounterGetResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model

from ..utils import UtilsMcounter, as_slow


@pytest.fixture()
def index_and_value(model_configuration: Dict[str, Any], request: SubRequest):
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


@pytest.mark.parametrize(
    "index_and_value",
    as_slow(UtilsMcounter.VALID_INDICES, 10),
    indirect=True,
)
def test_get_initialized_counter(
    index_and_value: Tuple[int, int], host: Host, model: Tropic01Model
):
    index, value = index_and_value
    assert model.r_mcounters[index].value == value

    command = TsL3McounterGetCommand(
        mcounter_index=index,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3McounterGetResult)
    assert result.mcounter_val.value == value


@pytest.mark.parametrize("mcounter_index", as_slow(UtilsMcounter.VALID_INDICES, 10))
def test_get_notset_counter(host: Host, model: Tropic01Model, mcounter_index: int):
    assert model.r_mcounters[mcounter_index].value == UtilsMcounter.DEFAULT_VALUE

    command = TsL3McounterGetCommand(
        mcounter_index=mcounter_index,
    )
    result = host.send_command(command)

    assert result.result.value == TsL3McounterGetResult.ResultEnum.COUNTER_INVALID
    assert model.r_mcounters[mcounter_index].value == UtilsMcounter.DEFAULT_VALUE


@pytest.mark.parametrize("mcounter_index", as_slow(UtilsMcounter.INVALID_INDICES, 10))
def test_invalid_index(host: Host, mcounter_index: int):
    command = TsL3McounterGetCommand(
        mcounter_index=mcounter_index,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.UNAUTHORIZED
