# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, Tuple

import pytest
from _pytest.fixtures import SubRequest

from tvl.api.l3_api import TsL3McounterInitCommand, TsL3McounterInitResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model

from ..utils import UtilsMcounter, as_slow


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
    yield idx, val, UtilsMcounter.get_valid_data()


@pytest.mark.parametrize(
    "prepare_data_ok",
    as_slow(UtilsMcounter.VALID_INDICES, 10),
    indirect=True,
)
def test_valid_value(
    prepare_data_ok: Tuple[int, int, int], host: Host, model: Tropic01Model
):
    index, previous_value, value = prepare_data_ok
    assert model.r_mcounters[index].value == previous_value

    command = TsL3McounterInitCommand(mcounter_index=index, mcounter_val=value)
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3McounterInitResult)
    assert model.r_mcounters[index].value == value


@pytest.fixture()
def prepare_data_ko(model_configuration: Dict[str, Any], request: SubRequest):
    model_configuration.update(
        {
            "r_mcounters": {
                (idx := request.param): {
                    "value": (val := UtilsMcounter.get_valid_data())
                }
            }
        }
    )
    yield idx, val, UtilsMcounter.get_invalid_data()


@pytest.mark.parametrize(
    "prepare_data_ko",
    as_slow(UtilsMcounter.VALID_INDICES, 10),
    indirect=True,
)
def test_invalid_value(
    prepare_data_ko: Tuple[int, int, int], host: Host, model: Tropic01Model
):
    index, previous_value, value = prepare_data_ko
    assert model.r_mcounters[index].value == previous_value

    command = TsL3McounterInitCommand(mcounter_index=index, mcounter_val=value)
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
    assert isinstance(result, TsL3McounterInitResult)
    assert model.r_mcounters[index].value == previous_value


@pytest.mark.parametrize("mcounter_index", as_slow(UtilsMcounter.INVALID_INDICES, 10))
def test_invalid_index(host: Host, mcounter_index: int):
    command = TsL3McounterInitCommand(
        mcounter_index=mcounter_index, mcounter_val=UtilsMcounter.get_valid_data()
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.UNAUTHORIZED
