# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os

from tvl.api.l3_api import TsL3MacAndDestroyCommand
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host

from ..base_test import BaseTestSecureChannel


class TestMutableFwEraseReq(BaseTestSecureChannel):
    def test_mutable_fw_update_req(self, host: Host):
        result = host.send_command(
            TsL3MacAndDestroyCommand(
                slot=os.urandom(1),
                padding=os.urandom(2),
                data_in=os.urandom(32),
            )
        )
        assert result.result.value == L3ResultFieldEnum.INVALID_CMD
