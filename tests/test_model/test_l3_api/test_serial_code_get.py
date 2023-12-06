import os

from tvl.api.l3_api import TsL3SerialCodeGetCommand, TsL3SerialCodeGetResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model

from ..base_test import BaseTestSecureChannel

SERIAL_CODE = os.urandom(32)


class TestSerialCodeGet(BaseTestSecureChannel):
    CONFIGURATION = {"model": {"serial_code": SERIAL_CODE}}

    def test_serial_code_get(self, host: Host, model: Tropic01Model):
        assert model.serial_code == SERIAL_CODE

        command = TsL3SerialCodeGetCommand()
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.OK
        assert isinstance(result, TsL3SerialCodeGetResult)
        assert result.serial_code.to_bytes() == SERIAL_CODE
