# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
import random
from contextlib import nullcontext
from typing import Any, ContextManager

import pytest

from tvl.targets.model.internal.user_data_partition import (
    INIT_VALUE,
    SLOT_SIZE_BYTES,
    DataLengthOverflow,
    SlotAlreadyWrittenError,
    UserDataPartition,
    UserDataSlot,
)


@pytest.mark.parametrize(
    "init_free, init_value, write_value, context, expected_free, expected_value",
    [
        pytest.param(
            True,
            b"",
            v := os.urandom(random.randint(1, SLOT_SIZE_BYTES)),
            nullcontext(),
            False,
            v,
            id="ok",
        ),
        pytest.param(
            f := True,
            b"",
            v := os.urandom(SLOT_SIZE_BYTES),
            nullcontext(),
            False,
            v,
            id="maxlength_data-ok",
        ),
        pytest.param(
            True,
            v := os.urandom(random.randint(1, SLOT_SIZE_BYTES)),
            b"",
            nullcontext(),
            False,
            v,
            id="empty_data-ok",
        ),
        pytest.param(
            f := False,
            v := os.urandom(random.randint(1, SLOT_SIZE_BYTES)),
            b"",
            pytest.raises(SlotAlreadyWrittenError),
            f,
            v,
            id="already_written-error",
        ),
        pytest.param(
            f := True,
            v := b"",
            os.urandom(SLOT_SIZE_BYTES + 1),
            pytest.raises(DataLengthOverflow),
            f,
            v,
            id="overflow-error",
        ),
    ],
)
def test_write(
    init_free: bool,
    init_value: bytes,
    write_value: bytes,
    context: ContextManager[Any],
    expected_free: bool,
    expected_value: bytes,
):
    user_data_slot = UserDataSlot(free=init_free, value=init_value)
    with context:
        user_data_slot.write(write_value)
    assert user_data_slot.free is expected_free
    assert user_data_slot.read() == user_data_slot.value == expected_value


def test_erase():
    user_data_slot = UserDataSlot(free=False, value=os.urandom(300))
    assert not user_data_slot.free
    assert user_data_slot.value != INIT_VALUE

    user_data_slot.erase()
    assert user_data_slot.free
    assert user_data_slot.value == INIT_VALUE


def test_dict():
    user_data_slot_dict = {"free": False, "value": os.urandom(SLOT_SIZE_BYTES)}
    user_data_dict = {(slot := random.randint(0, 10)): user_data_slot_dict}

    mcounters = UserDataPartition.from_dict(user_data_dict)
    assert mcounters.to_dict() == user_data_dict
    assert mcounters[slot].to_dict() == user_data_slot_dict
