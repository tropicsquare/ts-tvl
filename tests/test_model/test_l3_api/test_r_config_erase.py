# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
from typing import Any, Dict

import pytest

from tvl.api.l3_api import TsL3RConfigEraseCommand, TsL3RConfigEraseResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.configuration_object_impl import ConfigObjectRegisterAddressEnum
from tvl.targets.model.internal.configuration_object import (
    ENDIANESS,
    REGISTER_RESET_VALUE,
)
from tvl.targets.model.tropic01_model import Tropic01Model

R_CONFIG_CFG = {
    **{
        register: random.randint(0, 2**32 - 1)
        for register in ConfigObjectRegisterAddressEnum
    },
    # ensure that the users have the rights to erase all the r-config registers
    ConfigObjectRegisterAddressEnum.CFG_UAP_R_CONFIG_WRITE_ERASE: 0x0000_FFFF,
}


@pytest.fixture()
def model_configuration(model_configuration: Dict[str, Any]):
    model_configuration.update(
        {
            "r_config": {
                register.name.lower(): value for register, value in R_CONFIG_CFG.items()
            }
        }
    )
    yield model_configuration


@pytest.mark.parametrize("register", R_CONFIG_CFG.keys())
def test_r_config_erase(
    host: Host,
    model: Tropic01Model,
    register: ConfigObjectRegisterAddressEnum,
):
    command = TsL3RConfigEraseCommand()
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3RConfigEraseResult)
    assert model.r_config.read(register) == int.from_bytes(
        REGISTER_RESET_VALUE, ENDIANESS
    )
