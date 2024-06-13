# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os

from tvl.api.l3_api import TsL3MacAndDestroyCommand
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host


def test(host: Host):
    command = TsL3MacAndDestroyCommand(
        slot=os.urandom(1),
        data_in=os.urandom(32),
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.INVALID_CMD
