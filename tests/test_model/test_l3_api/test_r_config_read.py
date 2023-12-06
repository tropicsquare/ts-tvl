import random

import pytest

from tvl.api.l3_api import TsL3RConfigReadCommand, TsL3RConfigReadResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.configuration_object_impl import ConfigObjectRegisterAddressEnum
from tvl.targets.model.tropic01_model import Tropic01Model

from ..base_test import BaseTestSecureChannel
from ..utils import sample_outside

R_CONFIG_CFG = {
    **{
        register: random.randint(0, 2**32 - 1)
        for register in ConfigObjectRegisterAddressEnum
    },
    # ensure that the users have the rights to read all the r-config registers
    ConfigObjectRegisterAddressEnum.CFG_UAP_R_CONFIG_READ: 0x0000_FFFF,
}


class TestRConfigRead(BaseTestSecureChannel):
    CONFIGURATION = {
        "model": {
            "r_config": {
                register.name.lower(): value for register, value in R_CONFIG_CFG.items()
            }
        }
    }

    @pytest.mark.parametrize(
        "address, value",
        (pytest.param(a, v, id=f"{a!s}-{v:#x}") for a, v in R_CONFIG_CFG.items()),
    )
    def test_valid_address(
        self, host: Host, model: Tropic01Model, address: int, value: int
    ):
        assert model.r_config[address].value == value

        command = TsL3RConfigReadCommand(
            address=address,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.OK
        assert isinstance(result, TsL3RConfigReadResult)
        assert result.value.value == value

    @pytest.mark.parametrize(
        "address", sample_outside(ConfigObjectRegisterAddressEnum, 2, k=10)
    )
    def test_invalid_address(self, host: Host, address: int):
        command = TsL3RConfigReadCommand(
            address=address,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
