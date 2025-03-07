import random
from itertools import chain
from typing import Any, Dict

import pytest

from tvl.api.l3_api import TsL3IConfigReadCommand, TsL3IConfigReadResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.configuration_object_impl import ConfigObjectRegisterAddressEnum
from tvl.targets.model.tropic01_model import Tropic01Model

from ..utils import UtilsCo

I_CONFIG_CFG = {
    **{
        register: random.randint(0, 2**32 - 1)
        for register in ConfigObjectRegisterAddressEnum
    },
    # ensure that the users have the rights to read all the i-config registers
    ConfigObjectRegisterAddressEnum.CFG_UAP_I_CONFIG_READ: 0x0000_FFFF,
}


@pytest.fixture()
def model_configuration(model_configuration: Dict[str, Any]):
    model_configuration.update(
        {
            "i_config": {
                register.name.lower(): value for register, value in I_CONFIG_CFG.items()
            }
        }
    )
    yield model_configuration


@pytest.mark.parametrize(
    "address, value",
    (pytest.param(a, v, id=f"{a!s}-{v:#x}") for a, v in I_CONFIG_CFG.items()),
)
def test_valid_address(host: Host, model: Tropic01Model, address: int, value: int):
    assert model.i_config.read(address) == value

    result = host.send_command(TsL3IConfigReadCommand(address=address))

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3IConfigReadResult)
    assert result.value.value == value


@pytest.mark.parametrize(
    "address, expected_result",
    chain(
        (
            pytest.param(a, L3ResultFieldEnum.FAIL, id=f"{a:#x}")
            for a in UtilsCo.invalid_addresses_not_aligned(50)
        ),
        (
            pytest.param(a, L3ResultFieldEnum.UNAUTHORIZED, id=f"{a:#x}")
            for a in UtilsCo.invalid_addresses_out_of_range_aligned(50)
        ),
        (
            pytest.param(a, L3ResultFieldEnum.UNAUTHORIZED, id=f"{a:#x}")
            for a in UtilsCo.invalid_addresses_out_of_range_and_not_aligned(50)
        ),
    ),
)
def test_invalid_address(host: Host, address: int, expected_result: L3ResultFieldEnum):
    result = host.send_command(TsL3IConfigReadCommand(address=address))

    assert result.result.value == expected_result
