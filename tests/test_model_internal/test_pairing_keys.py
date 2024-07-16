# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
import random
from contextlib import nullcontext
from typing import Any, ContextManager

import pytest

from tvl.targets.model.internal.pairing_keys import (
    KEY_SIZE,
    PairingKeys,
    PairingKeySlot,
    SlotState,
    WrittenSlotError,
)


@pytest.mark.parametrize(
    "init_value, init_state, write_value, context, expected_value",
    [
        pytest.param(
            a := os.urandom(KEY_SIZE),
            SlotState.BLANK,
            b := os.urandom(KEY_SIZE),
            nullcontext(),
            b,
            id="ok",
        ),
        pytest.param(
            a := os.urandom(KEY_SIZE),
            SlotState.BLANK,
            os.urandom(KEY_SIZE - 1),
            pytest.raises(ValueError),
            a,
            id="wrong_size",
        ),
        pytest.param(
            a := os.urandom(KEY_SIZE),
            SlotState.WRITTEN,
            b := os.urandom(KEY_SIZE),
            pytest.raises(WrittenSlotError),
            a,
            id="already_written",
        ),
        pytest.param(
            a := os.urandom(KEY_SIZE),
            SlotState.INVALID,
            os.urandom(KEY_SIZE),
            pytest.raises(WrittenSlotError),
            a,
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
):
    pairing_key = PairingKeySlot(init_value, init_state)
    with context:
        pairing_key.write(write_value)
    assert pairing_key.value == expected_value


@pytest.mark.skip(reason="TODO")
def test_read():
    pass


@pytest.mark.skip(reason="TODO")
def test_invalidate():
    pass


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
