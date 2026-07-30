import os
import random
from contextlib import nullcontext
from typing import Any, ContextManager, Dict, Optional

import pytest
from pydantic import ValidationError

from tvl.targets.model.internal.pairing_keys import (
    KEY_SIZE,
    BlankSlotError,
    InvalidatedSlotError,
    PairingKeys,
    PairingKeySlot,
    PairingKeysModel,
    SlotState,
    WrittenSlotError,
)

VALUE = os.urandom(KEY_SIZE)


@pytest.mark.parametrize(
    "init_value, init_state, write_value, context, expected_value, expected_state",
    [
        pytest.param(
            a := os.urandom(KEY_SIZE),
            SlotState.BLANK,
            b := os.urandom(KEY_SIZE),
            nullcontext(),
            b,
            SlotState.WRITTEN,
            id="blank",
        ),
        pytest.param(
            a := os.urandom(KEY_SIZE),
            SlotState.BLANK,
            os.urandom(KEY_SIZE - 1),
            pytest.raises(ValueError),
            a,
            SlotState.BLANK,
            id="wrong_size",
        ),
        pytest.param(
            a := os.urandom(KEY_SIZE),
            SlotState.WRITTEN,
            b := os.urandom(KEY_SIZE),
            pytest.raises(WrittenSlotError),
            a,
            SlotState.WRITTEN,
            id="already_written",
        ),
        pytest.param(
            a := os.urandom(KEY_SIZE),
            SlotState.INVALID,
            os.urandom(KEY_SIZE),
            pytest.raises(WrittenSlotError),
            a,
            SlotState.INVALID,
            id="invalidated",
        ),
    ],
)
def test_write(
    init_value: bytes,
    init_state: SlotState,
    write_value: bytes,
    context: ContextManager[Any],
    expected_value: bytes,
    expected_state: SlotState,
):
    pairing_key = PairingKeySlot(init_value, init_state)
    with context:
        pairing_key.write(write_value)
    assert pairing_key.value == expected_value
    assert pairing_key.state is expected_state


@pytest.mark.parametrize(
    "init_value, init_state, context",
    [
        pytest.param(
            os.urandom(KEY_SIZE),
            SlotState.WRITTEN,
            nullcontext(),
            id="written",
        ),
        pytest.param(
            os.urandom(KEY_SIZE),
            SlotState.BLANK,
            pytest.raises(BlankSlotError),
            id="blank",
        ),
        pytest.param(
            os.urandom(KEY_SIZE),
            SlotState.INVALID,
            pytest.raises(InvalidatedSlotError),
            id="invalidated",
        ),
    ],
)
def test_read(
    init_value: bytes,
    init_state: SlotState,
    context: ContextManager[Any],
):
    pairing_key = PairingKeySlot(init_value, init_state)
    with context:
        assert pairing_key.read() == init_value
    assert pairing_key.value == init_value
    assert pairing_key.state is init_state


@pytest.mark.parametrize(
    "init_value, init_state, context, expected_value, expected_state",
    [
        pytest.param(
            os.urandom(KEY_SIZE),
            SlotState.WRITTEN,
            nullcontext(),
            b"",
            SlotState.INVALID,
            id="written",
        ),
        pytest.param(
            a := os.urandom(KEY_SIZE),
            SlotState.BLANK,
            pytest.raises(BlankSlotError),
            a,
            SlotState.BLANK,
            id="blank",
        ),
        pytest.param(
            os.urandom(KEY_SIZE),
            SlotState.INVALID,
            nullcontext(),
            b"",
            SlotState.INVALID,
            id="invalidated",
        ),
    ],
)
def test_invalidate(
    init_value: bytes,
    init_state: SlotState,
    context: ContextManager[Any],
    expected_value: bytes,
    expected_state: SlotState,
):
    pairing_key = PairingKeySlot(init_value, init_state)
    with context:
        pairing_key.invalidate()
    assert pairing_key.value == expected_value
    assert pairing_key.state is expected_state


def test_state():
    pairing_key = PairingKeySlot()
    pairing_key.value = b""
    assert pairing_key.state is SlotState.BLANK


def test_dict():
    pairing_key_slot_dict = {
        "value": os.urandom(KEY_SIZE),
        "state": random.choice(list(SlotState)),
    }
    pairing_key_dict = {(slot := random.randint(0, 10)): pairing_key_slot_dict}

    pairing_keys = PairingKeys.from_dict(pairing_key_dict)
    assert pairing_keys.to_dict() == pairing_key_dict
    assert pairing_keys[slot].to_dict() == pairing_key_slot_dict


@pytest.mark.parametrize(
    "slot_dict, context, expected_value, expected_state",
    [
        pytest.param(
            {"value": VALUE},
            nullcontext(),
            VALUE,
            SlotState.WRITTEN,
            id="value_only_is_written",
        ),
        pytest.param(
            {"value": VALUE, "state": SlotState.WRITTEN},
            nullcontext(),
            VALUE,
            SlotState.WRITTEN,
            id="written",
        ),
        pytest.param(
            {"value": VALUE, "state": "written"},
            nullcontext(),
            VALUE,
            SlotState.WRITTEN,
            id="state_as_str",
        ),
        pytest.param(
            {"value": b"", "state": SlotState.BLANK},
            nullcontext(),
            b"",
            SlotState.BLANK,
            id="blank_dumped_by_model",
        ),
        pytest.param(
            {"value": b"", "state": SlotState.INVALID},
            nullcontext(),
            b"",
            SlotState.INVALID,
            id="invalidated_dumped_by_model",
        ),
        pytest.param(
            {"state": SlotState.BLANK},
            nullcontext(),
            b"",
            SlotState.BLANK,
            id="blank_without_value",
        ),
        pytest.param(
            {"state": SlotState.INVALID},
            nullcontext(),
            b"",
            SlotState.INVALID,
            id="invalidated_without_value",
        ),
        # A full-size value on a blank or invalidated slot is accepted - the slot
        # dataclass allows the same combination - and is simply not readable.
        pytest.param(
            {"value": VALUE, "state": SlotState.INVALID},
            nullcontext(),
            VALUE,
            SlotState.INVALID,
            id="invalidated_with_value",
        ),
        # A partial value is never accepted, whatever the state: only an empty
        # value - the one the model dumps - is allowed to differ from KEY_SIZE.
        pytest.param(
            {"value": os.urandom(KEY_SIZE - 1), "state": SlotState.INVALID},
            pytest.raises(ValidationError),
            None,
            None,
            id="invalidated_with_partial_value",
        ),
        pytest.param(
            {"value": os.urandom(KEY_SIZE - 1), "state": SlotState.BLANK},
            pytest.raises(ValidationError),
            None,
            None,
            id="blank_with_partial_value",
        ),
        pytest.param(
            {"value": b"", "state": SlotState.WRITTEN},
            pytest.raises(ValidationError),
            None,
            None,
            id="written_without_value",
        ),
        pytest.param(
            {},
            pytest.raises(ValidationError),
            None,
            None,
            id="empty_slot_dict",
        ),
        pytest.param(
            {"value": os.urandom(KEY_SIZE - 1)},
            pytest.raises(ValidationError),
            None,
            None,
            id="value_too_short",
        ),
        pytest.param(
            {"value": os.urandom(KEY_SIZE + 1)},
            pytest.raises(ValidationError),
            None,
            None,
            id="value_too_long",
        ),
        pytest.param(
            {"value": "s" * KEY_SIZE},
            pytest.raises(ValidationError),
            None,
            None,
            id="value_not_bytes",
        ),
        pytest.param(
            {"value": VALUE, "state": "erased"},
            pytest.raises(ValidationError),
            None,
            None,
            id="unknown_state",
        ),
    ],
)
def test_model_validation(
    slot_dict: Dict[str, Any],
    context: ContextManager[Any],
    expected_value: Optional[bytes],
    expected_state: Optional[SlotState],
):
    slot = random.randint(0, 10)
    with context:
        pairing_keys = PairingKeys.from_dict(
            PairingKeysModel.parse_obj({slot: slot_dict}).dict()
        )
        assert pairing_keys[slot].value == expected_value
        assert pairing_keys[slot].state is expected_state


@pytest.mark.parametrize("state", list(SlotState))
def test_dumped_dict_is_valid_configuration(state: SlotState):
    """The dict dumped by the model must pass configuration validation.

    Invalidated and blank slots hold no value, which used to be rejected on
    reload since `value` was constrained to exactly KEY_SIZE bytes.
    """
    pairing_keys = PairingKeys()
    if state is SlotState.BLANK:
        # A handshake looks the slot up, and the partition being a defaultdict
        # this materializes a blank slot - see tropic01_l2_api_impl.py.
        _ = pairing_keys[(slot := random.randint(0, 10))]
    else:
        pairing_keys[(slot := random.randint(0, 10))].write(VALUE)
        if state is SlotState.INVALID:
            pairing_keys[slot].invalidate()

    dumped = pairing_keys.to_dict()
    assert dumped[slot]["state"] == state.value

    reloaded = PairingKeys.from_dict(PairingKeysModel.parse_obj(dumped).dict())
    assert reloaded[slot].state is state
    assert reloaded[slot].value == pairing_keys[slot].value
    assert reloaded.to_dict() == dumped
