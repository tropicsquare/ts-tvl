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
    return random.randint(0, 2**32 - 2)


def _get_value_iter() -> Iterator[int]:
    while True:
        yield _get_value()


@pytest.fixture()
def set_configuration_objects(
    model_configuration: Dict[str, Any], host_configuration: Dict[str, Any]
):
    pki = host_configuration["pairing_key_index"]
    bit = 2**pki
    val = bit << 24 + bit << 16 + bit << 8 + bit
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
def test_valid_address_slot_not_written(
    host: Host, model: Tropic01Model, address: int, value: int
):
    assert (_r := model.r_config[address]).value == _r.reset_value

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
        for a, v in zip(ConfigObjectRegisterAddressEnum, _get_value_iter())
    ),
)
def test_valid_address(host: Host, model: Tropic01Model, address: int, value: int):
    assert (_r := model.r_config[address]).value != _r.reset_value

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
def test_invalid_address_slot_not_written(host: Host, address: int):
    command = TsL3RConfigWriteCommand(
        address=address,
        value=_get_value(),
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL


@pytest.mark.usefixtures(set_configuration_objects.__name__)
@pytest.mark.parametrize(
    "address", sample_outside(ConfigObjectRegisterAddressEnum, 2, k=10)
)
def test_invalid_address(host: Host, address: int):
    command = TsL3RConfigWriteCommand(
        address=address,
        value=_get_value(),
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
