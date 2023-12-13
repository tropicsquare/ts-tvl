# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
import random

from tvl.targets.model.internal.command_buffer import CommandBuffer


def test_command_buffer():
    command = b"".join(
        (
            chunk_0 := os.urandom(len_chunk_0 := random.randint(1, 10)),
            chunk_1 := os.urandom(len_chunk_1 := random.randint(1, 10)),
            chunk_2 := os.urandom(len_chunk_2 := random.randint(1, 10)),
        )
    )
    len_command = len(command)

    buffer = CommandBuffer()

    buffer.initialize(len_command)
    assert buffer.total_size == len_command
    assert not buffer.is_empty()
    assert buffer.is_command_incomplete()

    already_received = buffer.received_size
    buffer.add_chunk(chunk_0)
    assert buffer.is_command_incomplete()
    assert buffer.received_size == already_received + len_chunk_0

    already_received = buffer.received_size
    buffer.add_chunk(chunk_1)
    assert buffer.is_command_incomplete()
    assert buffer.received_size == already_received + len_chunk_1

    already_received = buffer.received_size
    buffer.add_chunk(chunk_2 + os.urandom(random.randint(1, 10)))
    assert not buffer.is_command_incomplete()
    assert buffer.received_size == already_received + len_chunk_2
    assert buffer.received_size == buffer.total_size == len_command
    assert buffer.get_raw_command() == command

    buffer.reset()
    assert buffer.is_empty()
    assert not buffer.is_command_incomplete()
    assert buffer.received_size == 0
    assert buffer.total_size == 0
