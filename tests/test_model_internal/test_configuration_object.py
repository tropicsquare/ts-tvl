# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
import string

import pytest

from tvl.targets.model.configuration_object_impl import (
    ConfigObjectRegisterAddressEnum,
    ConfigurationObjectImpl,
)
from tvl.targets.model.internal.configuration_object import (  # AccessType,
    CONFIG_OBJECT_SIZE_BYTES,
    REGISTER_SIZE_BITS,
    REGISTER_SIZE_BYTES,
    AddressOutOfRangeError,
    ConfigObjectField,
    ConfigObjectRegister,
    ConfigurationObject,
)


@pytest.mark.parametrize("iteration", range(5))
def test_configuration_register(iteration: int):
    width = random.randint(1, REGISTER_SIZE_BITS)
    offset = random.randint(0, REGISTER_SIZE_BITS - width)
    reg_value = random.getrandbits(REGISTER_SIZE_BITS)
    mask = 2**width - 1

    class _Register(ConfigObjectRegister):
        x = ConfigObjectField(offset, width)

    class _ConfigObject(ConfigurationObject):
        def __init__(self, **kwargs: int) -> None:
            self.reg = _Register(self, 0)
            super().__init__(**kwargs)

    co = _ConfigObject(reg=reg_value)

    assert co.reg.value == reg_value
    assert co.reg.x == reg_value >> offset & mask


def test_configuration_object_equalities():
    c1 = ConfigurationObjectImpl()
    c2 = ConfigurationObjectImpl()

    assert c1 != {}
    assert c1 != 567
    assert c1 == c1
    assert c1 == c2

    reg_addr = random.choice(list(ConfigObjectRegisterAddressEnum))
    reg_value = c2.read(reg_addr)
    while (new_value := random.getrandbits(REGISTER_SIZE_BITS)) == reg_value:
        pass
    c2.write(reg_addr, new_value)

    assert c2 == c2
    assert c1 != c2


def test_configuration_object_and():
    c1 = ConfigurationObjectImpl()
    c2 = ConfigurationObjectImpl()

    for _, register in c1.registers():
        c1.write(register.address, random.getrandbits(REGISTER_SIZE_BITS))

    for _, register in c2.registers():
        c2.write(register.address, random.getrandbits(REGISTER_SIZE_BITS))

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
    assert reg.value == c.read(reg.address)

    # test non-existing address
    while (dummy_address := random.getrandbits(16)) < CONFIG_OBJECT_SIZE_BYTES:
        pass
    dummy_address += -dummy_address % REGISTER_SIZE_BYTES
    with pytest.raises(AddressOutOfRangeError):
        c.read(dummy_address)


def test_configuration_object_dict():
    c1 = ConfigurationObjectImpl()

    c1d1 = c1.to_dict()
    default_values = c1d1.values()
    assert c1d1
    assert ConfigurationObjectImpl.from_dict(c1d1) == c1

    for _, register in c1.registers():
        c1.write(register.address, random.getrandbits(REGISTER_SIZE_BITS))

    c1d2 = c1.to_dict()
    assert c1d2 != c1d1
    assert ConfigurationObjectImpl.from_dict(c1d2) == c1

    while (dummy_key := "".join(random.choices(string.ascii_letters, k=5))) in {
        name for name, _ in c1.registers()
    }:
        pass
    while (dummy_value := random.getrandbits(REGISTER_SIZE_BITS)) in default_values:
        pass

    c2 = ConfigurationObjectImpl.from_dict({dummy_key: dummy_value})
    for _, register in c2.registers():
        assert register.value != dummy_value


def test_configuration_object_bytes():
    c1 = ConfigurationObjectImpl()
    c1b1 = c1.to_bytes()

    for _, register in c1.registers():
        c1.write(register.address, random.getrandbits(REGISTER_SIZE_BITS))

    c1b2 = c1.to_bytes()

    assert c1b2 != c1b1

    c2 = ConfigurationObjectImpl.from_bytes(c1b2)
    assert c2 == c1
    assert c2.to_bytes() == c1b2
