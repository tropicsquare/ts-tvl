import os
import random
from contextlib import nullcontext
from typing import Any, ContextManager

import pytest

from tvl.targets.model.internal.pairing_keys import (
    KEY_SIZE,
    BlankSlotError,
    InvalidatedSlotError,
    PairingKeys,
    PairingKeySlot,
    SlotState,
    WrittenSlotError,
)


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
