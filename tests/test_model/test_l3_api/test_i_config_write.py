# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
from itertools import chain
from typing import Any, Dict, Iterator

import pytest

from tvl.api.l3_api import TsL3IConfigWriteCommand, TsL3IConfigWriteResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.configuration_object_impl import ConfigObjectRegisterAddressEnum
from tvl.targets.model.tropic01_model import Tropic01Model

from ..utils import UtilsCo

U32_MAX = 2**32 - 1

I_CONFIG_CFG = {
    **{
        register: random.randint(0, U32_MAX)
        for register in ConfigObjectRegisterAddressEnum
    },
    # ensure that the users have the rights to write all the i-config registers
    ConfigObjectRegisterAddressEnum.CFG_UAP_I_CONFIG_WRITE: 0x0000_FFFF,
}


def _valid_bit_index() -> Iterator[int]:
    while True:
        yield random.randint(0, 31)


def _invalid_bit_index() -> Iterator[int]:
    while True:
        yield random.randint(32, 255)


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
    "register, value, bit_index",
    (
        pytest.param(r, v, bi, id=f"{r!s}-{v:#x}-{bi}")
        for (r, v), bi in zip(I_CONFIG_CFG.items(), _valid_bit_index())
    ),
)
def test_valid_bit_index(
    host: Host,
    model: Tropic01Model,
    register: ConfigObjectRegisterAddressEnum,
    value: int,
    bit_index: int,
):
    assert model.i_config.read(register) == value

    command = TsL3IConfigWriteCommand(
        address=register.value,
        bit_index=bit_index,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3IConfigWriteResult)
    assert model.i_config.read(register) == value & (~(2**bit_index) & U32_MAX)


@pytest.mark.parametrize(
    "register, bit_index",
    (
        pytest.param(r, bi, id=f"{r!s}-{bi}")
        for r, bi in zip(I_CONFIG_CFG, _invalid_bit_index())
    ),
)
def test_invalid_bit_index(
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
def test_invalid_address(address: int, expected_result: L3ResultFieldEnum, host: Host):
    command = TsL3IConfigWriteCommand(
        address=address,
        bit_index=next(_valid_bit_index()),
    )
    result = host.send_command(command)

    assert result.result.value == expected_result
