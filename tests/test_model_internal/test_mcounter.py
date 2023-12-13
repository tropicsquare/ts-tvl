# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
from contextlib import nullcontext
from typing import Any, ContextManager

import pytest

from tvl.targets.model.internal.mcounter import (
    MCOUNTER_MAX_VAL,
    NOTSET_VALUE,
    MCounter,
    MCounterNotInitializedError,
    MCounters,
    MCounterUpdateError,
    MCounterWrongInitValueError,
)


@pytest.mark.parametrize(
    "value, context",
    [
        pytest.param(
            random.randint(0, MCOUNTER_MAX_VAL),
            nullcontext(),
            id="between_bounds",
        ),
        pytest.param(0, nullcontext(), id="min"),
        pytest.param(MCOUNTER_MAX_VAL, nullcontext(), id="max"),
        pytest.param(-1, pytest.raises(MCounterWrongInitValueError), id="underflow"),
        pytest.param(
            MCOUNTER_MAX_VAL + 1,
            pytest.raises(MCounterWrongInitValueError),
            id="overfow",
        ),
    ],
)
def test_init(value: int, context: ContextManager[Any]):
    with context:
        MCounter().init(value)


@pytest.mark.parametrize(
    "init_value, context, expected_value",
    [
        pytest.param(
            v := random.randint(1, MCOUNTER_MAX_VAL),
            nullcontext(),
            v - 1,
            id="ok",
        ),
        pytest.param(
            NOTSET_VALUE,
            pytest.raises(MCounterNotInitializedError),
            NOTSET_VALUE,
            id="not_initialized",
        ),
        pytest.param(0, pytest.raises(MCounterUpdateError), 0, id="negative"),
    ],
)
def test_update(init_value: int, context: ContextManager[Any], expected_value: int):
    mcounter = MCounter(init_value)
    with context:
        mcounter.update()
    assert mcounter.value == expected_value


@pytest.mark.parametrize(
    "init_value, context",
    [
        pytest.param(random.randint(0, MCOUNTER_MAX_VAL), nullcontext(), id="ok"),
        pytest.param(
            NOTSET_VALUE,
            pytest.raises(MCounterNotInitializedError),
            id="not_initialized",
        ),
    ],
)
def test_get(init_value: int, context: ContextManager[Any]):
    mcounter = MCounter(init_value)
    with context:
        assert mcounter.get() == init_value


def test_dict():
    mcounter_slot_dict = {"value": random.randint(0, MCOUNTER_MAX_VAL)}
    mcounters_dict = {(slot := random.randint(0, 10)): mcounter_slot_dict}

    mcounters = MCounters.from_dict(mcounters_dict)
    assert mcounters.to_dict() == mcounters_dict
    assert mcounters[slot].to_dict() == mcounter_slot_dict
