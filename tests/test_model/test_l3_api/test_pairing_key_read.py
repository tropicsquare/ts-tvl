# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
from random import sample
from typing import Any, Dict

import pytest

from tvl.api.l3_api import TsL3PairingKeyReadCommand, TsL3PairingKeyReadResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.internal.pairing_keys import BLANK_VALUE, INVALID_VALUE, KEY_SIZE

from ..utils import sample_outside

KEY_SLOTS = sample(lst := (1, 2, 3, 4), k=len(lst))
SECURE_CHANNEL_KEY_IDX, SET_KEY_IDX, BLANK_KEY_IDX, INVALID_KEY_IDX = KEY_SLOTS

SET_KEY = os.urandom(KEY_SIZE)


@pytest.fixture()
def configuration(configuration: Dict[str, Any]):
    # set the secure channel key to another index
    configuration["host"]["pairing_key_index"] = SECURE_CHANNEL_KEY_IDX
    configuration["model"]["i_pairing_keys"] = {
        SECURE_CHANNEL_KEY_IDX: {"value": configuration["host"]["s_h_pub"]},
        SET_KEY_IDX: {"value": SET_KEY},
        BLANK_KEY_IDX: {"value": BLANK_VALUE},
        INVALID_KEY_IDX: {"value": INVALID_VALUE},
    }
    yield configuration


@pytest.mark.parametrize(
    "slot, expected_new_value",
    [
        pytest.param(BLANK_KEY_IDX, BLANK_VALUE, id="blank_slot"),
        pytest.param(SET_KEY_IDX, SET_KEY, id="already_set_slot"),
        pytest.param(INVALID_KEY_IDX, INVALID_VALUE, id="invalid_slot"),
    ],
)
def test_read_key(host: Host, slot: int, expected_new_value: bytes):
    command = TsL3PairingKeyReadCommand(
        slot=slot,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3PairingKeyReadResult)
    assert result.s_hipub.to_bytes() == expected_new_value


@pytest.mark.parametrize("slot", sample_outside(KEY_SLOTS, 1, k=10))
def test_read_out_of_range_key_slot(host: Host, slot: int):
    command = TsL3PairingKeyReadCommand(
        slot=slot,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
