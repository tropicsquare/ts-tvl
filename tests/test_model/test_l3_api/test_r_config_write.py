# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
from typing import Any, Dict, Iterator

import pytest

from tests.test_model.utils import sample_outside
from tvl.api.l3_api import TsL3RConfigWriteCommand, TsL3RConfigWriteResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.configuration_object_impl import ConfigObjectRegisterAddressEnum
from tvl.targets.model.tropic01_model import Tropic01Model


def _get_value() -> int:
    # 0xFFFF_FFFF is the reset value, and we want to avoid it
    while (_value := random.getrandbits(32)) == 0xFFFF_FFFF:
        continue
    return _value


def _get_value_iter() -> Iterator[int]:
    while True:
        yield _get_value()


@pytest.fixture()
def set_configuration_objects(
    model_configuration: Dict[str, Any], host_configuration: Dict[str, Any]
):
    pki = host_configuration["pairing_key_index"]
    bit = 2**pki
    val = (bit << 24) + (bit << 16) + (bit << 8) + bit
    model_configuration["r_config"] = {
        reg_addr.name.lower(): _get_value() | val
        for reg_addr in ConfigObjectRegisterAddressEnum
    }


@pytest.mark.parametrize(
    "address, value",
    (
        pytest.param(a, v, id=f"{a!s}-{v:#x}")
        for a, v in zip(ConfigObjectRegisterAddressEnum, _get_value_iter())
    ),
)
def test_valid_address_slot_set_to_reset_value(
    address: int, value: int, host: Host, model: Tropic01Model
):
    assert (_r := model.r_config[address]).value == _r.reset_value

    command = TsL3RConfigWriteCommand(
        address=address,
        value=value,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3RConfigWriteResult)
    assert model.r_config[address].value == value


@pytest.mark.usefixtures(set_configuration_objects.__name__)
@pytest.mark.parametrize(
    "address, value",
    (
        pytest.param(a, v, id=f"{a!s}-{v:#x}")
        for a, v in zip(ConfigObjectRegisterAddressEnum, _get_value_iter())
    ),
)
def test_valid_address(address: int, value: int, host: Host, model: Tropic01Model):
    register = model.r_config[address]
    previous_value = register.value
    assert previous_value != register.reset_value

    command = TsL3RConfigWriteCommand(
        address=address,
        value=value,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
    assert register.value == previous_value


@pytest.mark.parametrize(
    "address, value",
    (
        pytest.param(a, v, id=f"{a!s}-{v:#x}")
        for a, v in zip(
            sample_outside(ConfigObjectRegisterAddressEnum, 2, k=10), _get_value_iter()
        )
    ),
)
def test_invalid_address_slot_set_to_reset_value(
    address: int, value: int, host: Host, model: Tropic01Model
):
    assert all(reg.value == reg.reset_value for _, reg in model.r_config.registers())

    command = TsL3RConfigWriteCommand(
        address=address,
        value=value,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL


@pytest.mark.usefixtures(set_configuration_objects.__name__)
@pytest.mark.parametrize(
    "address, value",
    (
        pytest.param(a, v, id=f"{a!s}-{v:#x}")
        for a, v in zip(
            sample_outside(ConfigObjectRegisterAddressEnum, 2, k=10), _get_value_iter()
        )
    ),
)
def test_invalid_address(address: int, value: int, host: Host, model: Tropic01Model):
    assert all(reg.value != reg.reset_value for _, reg in model.r_config.registers())

    command = TsL3RConfigWriteCommand(
        address=address,
        value=value,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
