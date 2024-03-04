# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
from typing import Any, Dict

import pytest

from tvl.api.l3_api import TsL3RConfigReadCommand, TsL3RConfigReadResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.configuration_object_impl import ConfigObjectRegisterAddressEnum
from tvl.targets.model.tropic01_model import Tropic01Model

from ..utils import sample_outside

R_CONFIG_CFG = {
    **{
        register: random.randint(0, 2**32 - 1)
        for register in ConfigObjectRegisterAddressEnum
    },
    # ensure that the users have the rights to read all the r-config registers
    ConfigObjectRegisterAddressEnum.CFG_UAP_R_CONFIG_READ: 0x0000_FFFF,
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


@pytest.mark.parametrize(
    "address, value",
    (pytest.param(a, v, id=f"{a!s}-{v:#x}") for a, v in R_CONFIG_CFG.items()),
)
def test_valid_address(host: Host, model: Tropic01Model, address: int, value: int):
    assert model.r_config[address].value == value

    result = host.send_command(TsL3RConfigReadCommand(address=address))

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3RConfigReadResult)
    assert result.value.value == value


@pytest.mark.parametrize(
    "address", sample_outside(ConfigObjectRegisterAddressEnum, nb_bytes=2, k=10)
)
def test_invalid_address(host: Host, address: int):
    result = host.send_command(TsL3RConfigReadCommand(address=address))

    assert result.result.value == L3ResultFieldEnum.FAIL
