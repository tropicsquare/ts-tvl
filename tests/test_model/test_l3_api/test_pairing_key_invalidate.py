import os
from typing import Any, Dict

import pytest

from tvl.api.l3_api import TsL3PairingKeyInvalidateCommand
from tvl.configuration_file_model import ModelConfigurationModel
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.internal.pairing_keys import KEY_SIZE, SlotState
from tvl.targets.model.tropic01_model import Tropic01Model

from ..utils import sample_from, sample_outside

KEY_SLOTS = sample_from((lst := TsL3PairingKeyInvalidateCommand.SlotEnum), k=4)
SECURE_CHANNEL_KEY_IDX, SET_KEY_IDX, BLANK_KEY_IDX, INVALID_KEY_IDX = KEY_SLOTS

SET_KEY = os.urandom(KEY_SIZE)


@pytest.fixture()
def configuration(configuration: Dict[str, Any]):
    # set the secure channel key to another index
    configuration["host"]["pairing_key_index"] = SECURE_CHANNEL_KEY_IDX
    configuration["model"]["i_pairing_keys"] = {
        SECURE_CHANNEL_KEY_IDX: {
            "value": configuration["host"]["s_h_pub"][SECURE_CHANNEL_KEY_IDX]
        },
        SET_KEY_IDX: {"value": SET_KEY},
        BLANK_KEY_IDX: {"state": SlotState.BLANK},
        INVALID_KEY_IDX: {"state": SlotState.INVALID},
    }
    yield configuration


@pytest.mark.parametrize(
    "slot, expected_new_value, result_field",
    [
        pytest.param(
            BLANK_KEY_IDX,
            b"",
            L3ResultFieldEnum.FAIL,
            id="blank_slot",
        ),
        pytest.param(
            SET_KEY_IDX,
            b"",
            L3ResultFieldEnum.OK,
            id="already_set_slot",
        ),
        pytest.param(
            INVALID_KEY_IDX,
            b"",
            L3ResultFieldEnum.OK,
            id="invalid_slot",
        ),
    ],
)
def test_invalidate(
    host: Host,
    model: Tropic01Model,
    slot: int,
    expected_new_value: bytes,
    result_field: int,
):
    command = TsL3PairingKeyInvalidateCommand(
        slot=slot,
    )
    result = host.send_command(command)

    assert result.result.value == result_field
    assert model.i_pairing_keys[slot].value == expected_new_value


def test_invalidate_then_reload_configuration(host: Host, model: Tropic01Model):
    """The configuration dumped after an invalidation stays loadable.

    `--configuration-out` writes what `model.to_dict()` returns, and that file is
    meant to be fed back to the server through `--configuration`.
    """
    result = host.send_command(TsL3PairingKeyInvalidateCommand(slot=SET_KEY_IDX))
    assert result.result.value == L3ResultFieldEnum.OK

    dumped = model.to_dict()
    assert dumped["i_pairing_keys"][SET_KEY_IDX] == {"value": b"", "state": "invalid"}

    reloaded = Tropic01Model.from_dict(
        ModelConfigurationModel.parse_obj(dumped).dict(exclude_none=True)
    )

    assert reloaded.i_pairing_keys[SET_KEY_IDX].state is SlotState.INVALID
    assert reloaded.i_pairing_keys[SET_KEY_IDX].value == b""
    assert reloaded.i_pairing_keys[BLANK_KEY_IDX].state is SlotState.BLANK
    assert reloaded.i_pairing_keys[INVALID_KEY_IDX].state is SlotState.INVALID


@pytest.mark.parametrize(
    "slot",
    (
        pytest.param(val, id=f"out_of_range_slot_{i}")
        for i, val in enumerate(
            sample_outside(TsL3PairingKeyInvalidateCommand.SlotEnum, 1, k=10)
        )
    ),
)
def test_invalidate_out_of_range_key_slot(host: Host, slot: int):
    command = TsL3PairingKeyInvalidateCommand(
        slot=slot,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.UNAUTHORIZED
