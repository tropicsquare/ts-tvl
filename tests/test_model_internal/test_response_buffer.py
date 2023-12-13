# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
import random

import pytest

from tvl.targets.model.internal.response_buffer import (
    MaxResendCountReachedError,
    ResponseBuffer,
)


@pytest.mark.parametrize(
    "resend_max_count",
    [
        pytest.param(0, id="no_resend"),
        pytest.param(1, id="resend_once"),
        pytest.param(random.randint(2, 10), id="resend_at_least_twice"),
    ],
)
def test_response_buffer(resend_max_count: int):
    response_0 = os.urandom(random.randint(1, 10))
    response_1 = os.urandom(random.randint(1, 10))
    response_2 = os.urandom(random.randint(1, 10))

    buffer = ResponseBuffer(resend_max_count)

    buffer.add(response_0)
    assert buffer.responses == [response_0]
    assert not buffer.is_empty()

    buffer.add([response_1, response_2])
    assert buffer.responses == [response_0, response_1, response_2]
    assert not buffer.is_empty()

    assert buffer.next() == response_0
    for _ in range(resend_max_count):
        assert buffer.latest() == response_0
    with pytest.raises(MaxResendCountReachedError):
        buffer.latest()
    assert not buffer.is_empty()

    assert buffer.next() == response_1
    for _ in range(resend_max_count - 1):
        assert buffer.latest() == response_1
    assert not buffer.is_empty()

    assert buffer.next() == response_2
    assert buffer.is_empty()
