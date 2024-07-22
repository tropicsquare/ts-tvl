# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
from typing import Any, Dict

import pytest

from tvl.api.l3_api import TsL3PairingKeyReadCommand, TsL3PairingKeyReadResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.internal.pairing_keys import KEY_SIZE, SlotState

from ..utils import sample_from, sample_outside

KEY_SLOTS = sample_from((lst := TsL3PairingKeyReadCommand.SlotEnum), k=4)
SECURE_CHANNEL_KEY_IDX, SET_KEY_IDX, BLANK_KEY_IDX, INVALID_KEY_IDX = KEY_SLOTS

SET_KEY = os.urandom(KEY_SIZE)


@pytest.fixture()
def configuration(configuration: Dict[str, Any]):
    # set the secure channel key to another index
    configuration["host"]["pairing_key_index"] = SECURE_CHANNEL_KEY_IDX
    configuration["model"]["i_pairing_keys"] = {
        SECURE_CHANNEL_KEY_IDX: {"value": configuration["host"]["s_h_pub"]},
        SET_KEY_IDX: {"value": SET_KEY},
        BLANK_KEY_IDX: {"state": SlotState.BLANK},
        INVALID_KEY_IDX: {"state": SlotState.INVALID},
    }
    yield configuration


@pytest.mark.parametrize(
    "slot, expected_value",
    [
        pytest.param(SET_KEY_IDX, SET_KEY, id="already_set_slot"),
    ],
)
def test_read_key(host: Host, slot: int, expected_value: bytes):
    command = TsL3PairingKeyReadCommand(
        slot=slot,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3PairingKeyReadResult)
    assert result.s_hipub.to_bytes() == expected_value


@pytest.mark.parametrize(
    "slot, expected_result",
    [
        pytest.param(
            BLANK_KEY_IDX,
            TsL3PairingKeyReadResult.ResultEnum.PAIRING_KEY_EMPTY,
            id="blank_slot",
        ),
        pytest.param(
            INVALID_KEY_IDX,
            TsL3PairingKeyReadResult.ResultEnum.PAIRING_KEY_INVALID,
            id="invalid_slot",
        ),
    ],
)
def test_read_key_error(host: Host, slot: int, expected_result: int):
    command = TsL3PairingKeyReadCommand(
        slot=slot,
    )
    result = host.send_command(command)
    assert result.result.value == expected_result


@pytest.mark.parametrize(
    "slot", sample_outside(TsL3PairingKeyReadCommand.SlotEnum, 1, k=10)
)
def test_read_out_of_range_key_slot(host: Host, slot: int):
    command = TsL3PairingKeyReadCommand(
        slot=slot,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.UNAUTHORIZED
