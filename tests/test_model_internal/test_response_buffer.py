import os
import random

from tvl.targets.model.internal.response_buffer import ResponseBuffer


def test_response_buffer():
    response_0 = os.urandom(random.randint(1, 10))
    response_1 = os.urandom(random.randint(1, 10))
    response_2 = os.urandom(random.randint(1, 10))

    buffer = ResponseBuffer()
    assert buffer.latest() == b""
    assert buffer.is_empty()

    buffer.add(response_0)
    assert buffer.latest() == b""
    assert buffer.responses == [response_0]
    assert not buffer.is_empty()

    buffer.add([response_1, response_2])
    assert buffer.latest() == b""
    assert buffer.responses == [response_0, response_1, response_2]
    assert not buffer.is_empty()

    assert buffer.next() == response_0
    for _ in range(random.randint(1, 10)):
        assert buffer.latest() == response_0
    assert not buffer.is_empty()

    assert buffer.next() == response_1
    for _ in range(random.randint(1, 10)):
        assert buffer.latest() == response_1
    assert not buffer.is_empty()

    assert buffer.next() == response_2
    for _ in range(random.randint(1, 10)):
        assert buffer.latest() == response_2
    assert buffer.is_empty()

    for _ in range(random.randint(1, 10)):
        assert buffer.latest() == response_2
