# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
import random
from typing import Any, Dict

import pytest

from tvl.api.l3_api import TsL3RandomValueGetCommand, TsL3RandomValueGetResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host

N_BYTES = random.randint(1, 256)
RANDOM_VALUE = os.urandom(N_BYTES)


@pytest.fixture()
def model_configuration(model_configuration: Dict[str, Any]):
    model_configuration.update({"debug_random_value": RANDOM_VALUE})
    yield model_configuration


def test(host: Host):
    command = TsL3RandomValueGetCommand(n_bytes=N_BYTES)
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3RandomValueGetResult)
    assert result.random_data.to_bytes() == RANDOM_VALUE
