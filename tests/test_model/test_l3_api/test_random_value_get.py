import os
import random

from tvl.api.l3_api import TsL3RandomValueGetCommand, TsL3RandomValueGetResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host

from ..base_test import BaseTestSecureChannel

N_BYTES = random.randint(1, 256)
RANDOM_VALUE = os.urandom(N_BYTES)


class TestRandomValueGet(BaseTestSecureChannel):
    CONFIGURATION = {"model": {"debug_random_value": RANDOM_VALUE}}

    def test_random_value_get(self, host: Host):
        command = TsL3RandomValueGetCommand(n_bytes=N_BYTES)
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.OK
        assert isinstance(result, TsL3RandomValueGetResult)
        assert result.random_data.to_bytes() == RANDOM_VALUE
