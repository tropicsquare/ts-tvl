# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
import random
from contextlib import nullcontext
from typing import Any, ContextManager

import pytest

from tvl.targets.model.internal.pairing_keys import (
    BLANK_VALUE,
    INVALID_VALUE,
    KEY_SIZE,
    InvalidatedSlotError,
    PairingKeys,
    PairingKeySlot,
)


def _and(x: bytes, y: bytes) -> bytes:
    return (
        int.from_bytes(x, byteorder="big") & int.from_bytes(y, byteorder="big")
    ).to_bytes(KEY_SIZE, byteorder="big")


@pytest.mark.parametrize(
    "init_value, write_value, context, expected_value",
    [
        pytest.param(
            a := os.urandom(KEY_SIZE),
            b := os.urandom(KEY_SIZE),
            nullcontext(),
            _and(a, b),
            id="ok",
        ),
        pytest.param(
            0,
            os.urandom(KEY_SIZE - 1),
            pytest.raises(ValueError),
            0,
            id="wrong_size",
        ),
        pytest.param(
            INVALID_VALUE,
            os.urandom(KEY_SIZE),
            pytest.raises(InvalidatedSlotError),
            INVALID_VALUE,
            id="invalidated",
        ),
    ],
)
def test_write(
    init_value: bytes,
    write_value: bytes,
    context: ContextManager[Any],
    expected_value: bytes,
):
    pairing_key = PairingKeySlot(init_value)
    with context:
        pairing_key.write(write_value)
    assert pairing_key.read() == expected_value


def test_state():
    pairing_key = PairingKeySlot()
    pairing_key.value = BLANK_VALUE
    assert pairing_key.is_blank()
    assert not pairing_key.is_invalidated()

    pairing_key.value = INVALID_VALUE
    assert not pairing_key.is_blank()
    assert pairing_key.is_invalidated()


def test_dict():
    pairing_key_slot_dict = {"value": os.urandom(KEY_SIZE)}
    pairing_key_dict = {(slot := random.randint(0, 10)): pairing_key_slot_dict}

    pairing_keys = PairingKeys.from_dict(pairing_key_dict)
    assert pairing_keys.to_dict() == pairing_key_dict
    assert pairing_keys[slot].to_dict() == pairing_key_slot_dict
