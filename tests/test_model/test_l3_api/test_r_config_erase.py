# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random

import pytest

from tvl.api.l3_api import TsL3RConfigEraseCommand, TsL3RConfigEraseResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.configuration_object_impl import ConfigObjectRegisterAddressEnum
from tvl.targets.model.tropic01_l3_api_impl import (
    CONFIGURATION_ACCESS_PRIVILEGES,
    FUNCTIONALITY_ACCESS_PRIVILEGES,
)
from tvl.targets.model.tropic01_model import Tropic01Model

from ..base_test import BaseTestSecureChannel

R_CONFIG_CFG = {
    **{
        register: random.randint(0, 2**32 - 1)
        for register in FUNCTIONALITY_ACCESS_PRIVILEGES
        + CONFIGURATION_ACCESS_PRIVILEGES
    },
    # ensure that the users have the rights to erase all the r-config registers
    ConfigObjectRegisterAddressEnum.CFG_UAP_R_CONFIG_ERASE: 0x0000_FFFF,
}


class TestRConfigErase(BaseTestSecureChannel):
    CONFIGURATION = {
        "model": {
            "r_config": {
                register.name.lower(): value for register, value in R_CONFIG_CFG.items()
            }
        }
    }

    @pytest.mark.parametrize("register", R_CONFIG_CFG.keys())
    def test_r_config_erase(
        self,
        host: Host,
        model: Tropic01Model,
        register: ConfigObjectRegisterAddressEnum,
    ):
        command = TsL3RConfigEraseCommand()
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.OK
        assert isinstance(result, TsL3RConfigEraseResult)
        assert (_r := model.r_config[register.value]).value == _r.reset_value
