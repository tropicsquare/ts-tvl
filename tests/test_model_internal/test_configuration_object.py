# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
import string

import pytest

from tvl.targets.model.configuration_object_impl import ConfigurationObjectImpl
from tvl.targets.model.internal.configuration_object import (
    REGISTER_SIZE,
    AccessType,
    ConfigObjectField,
    ConfigObjectRegister,
)


@pytest.mark.parametrize(
    "access_type, current, expected",
    [
        pytest.param((ac := AccessType.RW), (a := 0b0101), a, id=f"{ac}"),
        pytest.param((ac := AccessType.RO), a, a, id=f"{ac}"),
        pytest.param((ac := AccessType.WO), a, 0, id=f"{ac}"),
        pytest.param((ac := AccessType.W1C), a, a, id=f"{ac}"),
        pytest.param((ac := AccessType.W0C), a, a, id=f"{ac}"),
        pytest.param((ac := AccessType.W1S), a, a, id=f"{ac}"),
        pytest.param((ac := AccessType.W0S), a, a, id=f"{ac}"),
        pytest.param((ac := AccessType.W1T), a, a, id=f"{ac}"),
        pytest.param((ac := AccessType.W0T), a, a, id=f"{ac}"),
    ],
)
def test_access_types_read(access_type: AccessType, current: int, expected: int):
    assert access_type.read(current) == expected


@pytest.mark.parametrize(
    "access_type, current, new, expected",
    [
        pytest.param(
            (ac := AccessType.RW), (a := 0b0101), (b := 0b1100), b, id=f"{ac}"
        ),
        pytest.param((ac := AccessType.RO), a, b, a, id=f"{ac}"),
        pytest.param((ac := AccessType.WO), a, b, b, id=f"{ac}"),
        pytest.param((ac := AccessType.W1C), a, b, 0b0001, id=f"{ac}"),
        pytest.param((ac := AccessType.W0C), a, b, 0b0100, id=f"{ac}"),
        pytest.param((ac := AccessType.W1S), a, b, 0b1101, id=f"{ac}"),
        pytest.param((ac := AccessType.W0S), a, b, 0b0111, id=f"{ac}"),
        pytest.param((ac := AccessType.W1T), a, b, 0b1001, id=f"{ac}"),
        pytest.param((ac := AccessType.W0T), a, b, 0b0110, id=f"{ac}"),
    ],
)
def test_access_types_write(
    access_type: AccessType, current: int, new: int, expected: int
):
    assert access_type.write(current, new, 0b1111) == expected


@pytest.mark.parametrize("iteration", range(5))
def test_configuration_register(iteration: int):
    width = random.randint(1, REGISTER_SIZE)
    offset = random.randint(0, REGISTER_SIZE - width)
    while (ac := random.choice(list(iter(AccessType)))) is AccessType.WO:
        pass
    reg_value = random.getrandbits(REGISTER_SIZE)

    mask = 2**width - 1
    field_mask = ~(mask << offset) & 0xFFFF_FFFF

    class _Register(ConfigObjectRegister):
        x = ConfigObjectField(offset, width, ac)

    reg = _Register(0, reg_value)

    assert reg.value == reg_value
    assert reg.x == ac.read(reg_value) >> offset & mask
    field_value = reg_value >> offset & mask

    value = random.getrandbits(width)
    new_field_value = ac.write(field_value, value, mask)
    reg.x = value
    assert reg.x == new_field_value

    new_reg_value = reg_value & field_mask | new_field_value << offset
    assert reg.value == new_reg_value


def test_configuration_object_equalities():
    c1 = ConfigurationObjectImpl()
    c2 = ConfigurationObjectImpl()

    assert c1 != {}
    assert c1 != 567
    assert c1 == c1
    assert c1 == c2


def test_configuration_object_and():
    c1 = ConfigurationObjectImpl()
    c2 = ConfigurationObjectImpl()

    for _, register in c2.registers():
        register.value = random.getrandbits(REGISTER_SIZE)

    ref_dict = {
        regname: getattr(c1, regname).value & getattr(c2, regname).value
        for regname, _ in c1.registers()
    }
    c3 = c1 & c2
    assert c3 != c1
    assert c3 != c2
    assert c3.to_dict() == ref_dict

    with pytest.raises(TypeError):
        c3 = c1 & 12


def test_configuration_object_getitem():
    c = ConfigurationObjectImpl()

    # test existing address
    reg = random.choice([reg for _, reg in c.registers()])
    assert reg is c[reg.address]

    # test non-existing address
    possible_addresses = [reg.address for _, reg in c.registers()]
    while (dummy_address := random.getrandbits(8)) in possible_addresses:
        pass
    with pytest.raises(IndexError):
        c[dummy_address]


def test_configuration_object_dict():
    c1 = ConfigurationObjectImpl()

    c1d1 = c1.to_dict()
    default_values = c1d1.values()
    assert c1d1
    assert ConfigurationObjectImpl.from_dict(c1d1) == c1

    for _, register in c1.registers():
        register.value = random.getrandbits(REGISTER_SIZE)

    c1d2 = c1.to_dict()
    assert c1d2 != c1d1
    assert ConfigurationObjectImpl.from_dict(c1d2) == c1

    while (dummy_key := "".join(random.choices(string.ascii_letters, k=5))) in {
        name for name, _ in c1.registers()
    }:
        pass
    while (dummy_value := random.getrandbits(REGISTER_SIZE)) in default_values:
        pass

    c2 = ConfigurationObjectImpl.from_dict({dummy_key: dummy_value})
    for _, register in c2.registers():
        assert register.value != dummy_value


def test_configuration_object_bytes():
    c1 = ConfigurationObjectImpl()
    c1b1 = c1.to_bytes()

    for _, register in c1.registers():
        register.value = random.getrandbits(REGISTER_SIZE)

    c1b2 = c1.to_bytes()

    assert c1b2 != c1b1

    c2 = ConfigurationObjectImpl.from_bytes(c1b2)
    assert c2 == c1
    assert c2.to_bytes() == c1b2
