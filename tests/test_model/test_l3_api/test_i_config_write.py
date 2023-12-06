import random
from itertools import count

import pytest

from tests.test_model.utils import sample_outside
from tvl.api.l3_api import TsL3IConfigWriteCommand, TsL3IConfigWriteResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.configuration_object_impl import ConfigObjectRegisterAddressEnum
from tvl.targets.model.tropic01_model import Tropic01Model

from ..base_test import BaseTestSecureChannel

U32_MAX = 2**32 - 1

I_CONFIG_CFG = {
    **{
        register: random.randint(0, U32_MAX)
        for register in ConfigObjectRegisterAddressEnum
    },
    # ensure that the users have the rights to write all the i-config registers
    ConfigObjectRegisterAddressEnum.CFG_UAP_I_CONFIG_WRITE: 0x0000_FFFF,
}


def _valid_bit_index() -> int:
    return random.randint(0, 31)


def _invalid_bit_index() -> int:
    return random.randint(32, 255)


class TestIConfigWrite(BaseTestSecureChannel):
    CONFIGURATION = {
        "model": {
            "i_config": {
                register.name.lower(): value for register, value in I_CONFIG_CFG.items()
            }
        }
    }

    @pytest.mark.parametrize(
        "register, value, bit_index",
        (
            pytest.param(r, v, bi, id=f"{r!s}-{v:#x}-{bi}")
            for (r, v), bi in zip(
                I_CONFIG_CFG.items(), (_valid_bit_index() for _ in count())
            )
        ),
    )
    def test_valid_bit_index(
        self,
        host: Host,
        model: Tropic01Model,
        register: ConfigObjectRegisterAddressEnum,
        value: int,
        bit_index: int,
    ):
        assert model.i_config[register.value].value == value

        command = TsL3IConfigWriteCommand(
            address=register.value,
            bit_index=bit_index,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.OK
        assert isinstance(result, TsL3IConfigWriteResult)
        assert model.i_config[register.value].value == value & (
            ~(2**bit_index) & U32_MAX
        )

    @pytest.mark.parametrize(
        "register, bit_index",
        (
            pytest.param(r, bi, id=f"{r!s}-{bi}")
            for r, bi in zip(I_CONFIG_CFG, (_invalid_bit_index() for _ in count()))
        ),
    )
    def test_invalid_bit_index(
        self,
        host: Host,
        register: ConfigObjectRegisterAddressEnum,
        bit_index: int,
    ):
        command = TsL3IConfigWriteCommand(
            address=register.value,
            bit_index=bit_index,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL

    @pytest.mark.parametrize(
        "address", sample_outside(ConfigObjectRegisterAddressEnum, 2, k=10)
    )
    def test_invalid_address(self, host: Host, address: int):
        command = TsL3IConfigWriteCommand(
            address=address,
            bit_index=_valid_bit_index(),
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
