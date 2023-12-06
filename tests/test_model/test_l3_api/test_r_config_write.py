import random
from itertools import count

import pytest

from tests.test_model.utils import sample_outside
from tvl.api.l3_api import TsL3RConfigWriteCommand, TsL3RConfigWriteResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.configuration_object_impl import ConfigObjectRegisterAddressEnum
from tvl.targets.model.tropic01_model import Tropic01Model

from ..base_test import BaseTestSecureChannel


class TestRConfigWrite(BaseTestSecureChannel):
    @pytest.mark.parametrize(
        "address, value",
        (
            pytest.param(a, v, id=f"{a!s}-{v:#x}")
            for a, v in zip(
                ConfigObjectRegisterAddressEnum,
                (random.randint(0, 2**32 - 1) for _ in count()),
            )
        ),
    )
    def test_valid_address(
        self, host: Host, model: Tropic01Model, address: int, value: int
    ):
        assert model.r_config[address].value == model.r_config[address].reset_value

        command = TsL3RConfigWriteCommand(
            address=address,
            value=value,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.OK
        assert isinstance(result, TsL3RConfigWriteResult)
        assert model.r_config[address].value == value

    @pytest.mark.parametrize(
        "address", sample_outside(ConfigObjectRegisterAddressEnum, 2, k=10)
    )
    def test_invalid_address(self, host: Host, address: int):
        command = TsL3RConfigWriteCommand(
            address=address,
            value=random.randint(0, 2**32 - 1),
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.FAIL
