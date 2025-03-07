from itertools import chain
from typing import Any, Dict

import pytest

from tvl.api.l3_api import TsL3RConfigWriteCommand, TsL3RConfigWriteResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.configuration_object_impl import ConfigObjectRegisterAddressEnum
from tvl.targets.model.internal.configuration_object import (
    ENDIANESS,
    REGISTER_RESET_VALUE,
)
from tvl.targets.model.tropic01_model import Tropic01Model

from ..utils import UtilsCo

# U16_MAX = 2**16


# def _get_value() -> int:
#     # 0xFFFF_FFFF is the reset value, and we want to avoid it
#     while (_value := random.getrandbits(32)) == 0xFFFF_FFFF:
#         continue
#     return _value


# def UtilsCo.get_value_iter() -> Iterator[int]:
#     while True:
#         yield _get_value()


# def _valid_addresses() -> Iterator[int]:
#     yield from range(0, CONFIG_OBJECT_SIZE_BYTES, REGISTER_SIZE_BYTES)


# def _invalid_addresses_not_aligned(k: int) -> Iterator[int]:
#     for _ in range(k):
#         while (address := random.randrange(1, CONFIG_OBJECT_SIZE_BYTES)) % REGISTER_SIZE_BYTES == 0:
#             continue
#         yield address


# def _invalid_addresses_out_of_range_aligned(k: int) -> Iterator[int]:
#     for _ in range(k):
#         while (address := random.randrange(CONFIG_OBJECT_SIZE_BYTES, U16_MAX)) % REGISTER_SIZE_BYTES != 0:
#             continue
#         yield address


# def _invalid_addresses_out_of_range_and_not_aligned(k: int) -> Iterator[int]:
#     for _ in range(k):
#         while (address := random.randrange(CONFIG_OBJECT_SIZE_BYTES, U16_MAX)) % REGISTER_SIZE_BYTES == 0:
#             continue
#         yield address


@pytest.fixture()
def set_configuration_objects(
    model_configuration: Dict[str, Any], host_configuration: Dict[str, Any]
):
    pki = host_configuration["pairing_key_index"]
    bit = 2**pki
    val = (bit << 24) + (bit << 16) + (bit << 8) + bit
    model_configuration["r_config"] = {
        reg_addr.name.lower(): UtilsCo.get_value() | val
        for reg_addr in ConfigObjectRegisterAddressEnum
    }


@pytest.mark.parametrize(
    "address, value",
    (
        pytest.param(a, v, id=f"{a:#x}-{v:#x}")
        for a, v in zip(UtilsCo.valid_addresses(), UtilsCo.get_value_iter())
    ),
)
def test_valid_address_slot_set_to_reset_value(
    address: int, value: int, host: Host, model: Tropic01Model
):
    assert model.r_config.read(address) == int.from_bytes(
        REGISTER_RESET_VALUE, ENDIANESS
    )

    command = TsL3RConfigWriteCommand(
        address=address,
        value=value,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3RConfigWriteResult)
    assert model.r_config.read(address) == value


@pytest.mark.usefixtures(set_configuration_objects.__name__)
@pytest.mark.parametrize(
    "address, value",
    (
        pytest.param(a, v, id=f"{a!s}-{v:#x}")
        for a, v in zip(ConfigObjectRegisterAddressEnum, UtilsCo.get_value_iter())
    ),
)
def test_valid_address(address: int, value: int, host: Host, model: Tropic01Model):
    previous_value = model.r_config.read(address)
    assert previous_value != int.from_bytes(REGISTER_RESET_VALUE, ENDIANESS)

    command = TsL3RConfigWriteCommand(
        address=address,
        value=value,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
    assert model.r_config.read(address) == previous_value


@pytest.mark.parametrize(
    "address, value, expected_result",
    (
        *(
            pytest.param(a, v, L3ResultFieldEnum.FAIL, id=f"{a:#x}-{v:#x}")
            for a, v in zip(
                UtilsCo.invalid_addresses_not_aligned(10), UtilsCo.get_value_iter()
            )
        ),
        *(
            pytest.param(a, v, L3ResultFieldEnum.UNAUTHORIZED, id=f"{a:#x}-{v:#x}")
            for a, v in zip(
                UtilsCo.invalid_addresses_out_of_range_aligned(10),
                UtilsCo.get_value_iter(),
            )
        ),
        *(
            pytest.param(a, v, L3ResultFieldEnum.UNAUTHORIZED, id=f"{a:#x}-{v:#x}")
            for a, v in zip(
                UtilsCo.invalid_addresses_out_of_range_and_not_aligned(10),
                UtilsCo.get_value_iter(),
            )
        ),
    ),
)
def test_invalid_address_slot_set_to_reset_value(
    address: int,
    value: int,
    expected_result: L3ResultFieldEnum,
    host: Host,
    model: Tropic01Model,
):
    assert all(
        reg.value == int.from_bytes(REGISTER_RESET_VALUE, ENDIANESS)
        for _, reg in model.r_config.registers()
    )

    command = TsL3RConfigWriteCommand(
        address=address,
        value=value,
    )
    result = host.send_command(command)

    assert result.result.value == expected_result


@pytest.mark.usefixtures(set_configuration_objects.__name__)
@pytest.mark.parametrize(
    "address, value, expected_result",
    chain(
        (
            pytest.param(a, v, L3ResultFieldEnum.FAIL, id=f"{a:#x}-{v:#x}")
            for a, v in zip(
                UtilsCo.invalid_addresses_not_aligned(50), UtilsCo.get_value_iter()
            )
        ),
        (
            pytest.param(a, v, L3ResultFieldEnum.UNAUTHORIZED, id=f"{a:#x}-{v:#x}")
            for a, v in zip(
                UtilsCo.invalid_addresses_out_of_range_aligned(50),
                UtilsCo.get_value_iter(),
            )
        ),
        (
            pytest.param(a, v, L3ResultFieldEnum.UNAUTHORIZED, id=f"{a:#x}-{v:#x}")
            for a, v in zip(
                UtilsCo.invalid_addresses_out_of_range_and_not_aligned(50),
                UtilsCo.get_value_iter(),
            )
        ),
    ),
)
def test_invalid_address(
    address: int,
    value: int,
    expected_result: L3ResultFieldEnum,
    host: Host,
    model: Tropic01Model,
):
    assert all(
        reg.value != int.from_bytes(REGISTER_RESET_VALUE, ENDIANESS)
        for _, reg in model.r_config.registers()
    )

    command = TsL3RConfigWriteCommand(
        address=address,
        value=value,
    )
    result = host.send_command(command)

    assert result.result.value == expected_result
