# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os

import pytest

from tvl.api.l3_api import TsL3PingCommand, TsL3PingResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host

from ..utils import as_slow


@pytest.mark.parametrize("data_in", as_slow([os.urandom(i) for i in range(33)], 10))
def test(host: Host, data_in: bytes):
    command = TsL3PingCommand(data_in=data_in)
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3PingResult)
    assert result.data_out.to_bytes() == data_in


# TODO add tests with no rights
