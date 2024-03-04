# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
from typing import Any, Dict

import pytest

from tvl.api.l3_api import TsL3SerialCodeGetCommand, TsL3SerialCodeGetResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model

SERIAL_CODE = os.urandom(32)


@pytest.fixture()
def model_configuration(model_configuration: Dict[str, Any]):
    model_configuration.update({"serial_code": SERIAL_CODE})
    yield model_configuration


def test(host: Host, model: Tropic01Model):
    assert model.serial_code == SERIAL_CODE

    command = TsL3SerialCodeGetCommand()
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3SerialCodeGetResult)
    assert result.serial_code.to_bytes() == SERIAL_CODE
