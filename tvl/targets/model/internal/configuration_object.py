# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import contextlib
from enum import Enum
from itertools import count, islice
from typing import Any, Callable, Dict, Iterator, Mapping, Tuple

from pydantic import BaseModel, root_validator
from typing_extensions import Self

CONFIG_OBJECT_SIZE_BYTES = 512
REGISTER_SIZE = 32
REGISTER_SIZE_BYTES = 32 // 8
REGISTER_MASK = 2**REGISTER_SIZE - 1


class AccessType(Enum):
    """Registers' access types"""

    RW = (lambda x: x, lambda x, y, m: y)  # type: ignore
    """Read-Write ﬁeld"""
    RO = (lambda x: x, lambda x, y, m: x)  # type: ignore
    """Read-only ﬁeld"""
    WO = (lambda x: 0, lambda x, y, m: y)  # type: ignore
    """Write-only ﬁeld"""
    W1C = (lambda x: x, lambda x, y, m: x & (~y & m))  # type: ignore
    """Write 1 to clear"""
    W0C = (lambda x: x, lambda x, y, m: x & y)  # type: ignore
    """Write 0 to clear"""
    W1S = (lambda x: x, lambda x, y, m: x | y)  # type: ignore
    """Write 1 to set"""
    W0S = (lambda x: x, lambda x, y, m: x | (~y & m))  # type: ignore
    """Write 0 to set"""
    W1T = (lambda x: x, lambda x, y, m: x ^ y)  # type: ignore
    """Write 1 to toggle"""
    W0T = (lambda x: x, lambda x, y, m: x ^ (~y & m))  # type: ignore
    """Write 0 to toggle"""

    def __init__(
        self,
        read_function: Callable[[int], int],
        write_function: Callable[[int, int, int], int],
    ) -> None:
        self.read_function = read_function
        self.write_function = write_function

    def read(self, value: int) -> int:
        """Behavior upon read access

        Args:
            value (int): current register's value

        Returns:
            the register's value when read
        """
        return self.read_function(value)

    def write(self, value: int, new_value: int, mask: int) -> int:
        """Behavior upon write access

        Args:
            value (int): current register's value
            new_value (int): new value to write
            mask (int): mask of the register

        Returns:
            the register's value as actually written
        """
        return self.write_function(value, new_value, mask)

    def __repr__(self) -> str:
        return str(self)


class ConfigObjectRegister:
    """Register contained in a configuration object"""

    def __init__(self, address: int, reset_value: int) -> None:
        self.address = address
        self.reset_value = reset_value
        self.reset()

    def reset(self) -> None:
        self.value = self.reset_value

    def write_bit(self, bit_index: int) -> None:
        if not 0 <= bit_index < REGISTER_SIZE:
            raise ValueError(f"Bit index is out of bound: {bit_index}")
        masked_value = ~(2**bit_index) & REGISTER_MASK
        self.value &= masked_value


class ConfigObjectField:
    """Register's field"""

    def __init__(
        self,
        offset: int,
        width: int,
        access_type: AccessType = AccessType.W1C,
    ) -> None:
        self.offset = offset
        self.mask = 2**width - 1
        self.access_type = access_type

    def __get__(self, instance: ConfigObjectRegister, _) -> int:
        return self.access_type.read(instance.value >> self.offset & self.mask)

    def __set__(self, instance: ConfigObjectRegister, value: int) -> None:
        reg_value = instance.value

        current_value = reg_value >> self.offset & self.mask
        new_value = self.access_type.write(current_value, value, self.mask)

        field_mask = ~(self.mask << self.offset) & REGISTER_MASK
        instance.value = reg_value & field_mask | new_value << self.offset


class ConfigurationObject:
    """Chip configuration abstraction"""

    def __init__(self, **kwargs: int) -> None:
        for regname, register in self.registers():
            with contextlib.suppress(KeyError):
                register.value = kwargs[regname]

    def registers(self) -> Iterator[Tuple[str, ConfigObjectRegister]]:
        """Go over the registers of the configuration object.

        Returns:
            an iterator of the registers in the configuration object
        """
        for key, value in self.__dict__.items():
            if isinstance(value, ConfigObjectRegister):
                yield key, value

    def __getitem__(self, __item: int) -> ConfigObjectRegister:
        for _, register in self.registers():
            if register.address == __item:
                return register
        raise IndexError(f"Index {__item:#x} out of range")

    def __and__(self, __other: Any) -> Self:
        if not isinstance(__other, self.__class__):
            return NotImplemented
        new_instance = self.__class__()
        for regname, _ in self.registers():
            new_instance.__dict__[regname].value = (
                self.__dict__[regname].value & __other.__dict__[regname].value
            )
        return new_instance

    def __str__(self) -> str:
        registers = "; ".join(
            f"{regname}={register.value:#010x}"
            for regname, register in self.registers()
        )
        return f"{self.__class__.__name__}({registers})"

    def __eq__(self, __other: Any, /) -> bool:
        if __other is self:
            return True
        if not isinstance(__other, self.__class__):
            return NotImplemented
        return all(
            self.__dict__[regname].value == __other.__dict__[regname].value
            for regname, _ in self.registers()
        )

    def to_dict(self) -> Dict[str, int]:
        """Save the configuration object content.

        Returns:
            the content of the configuration object
        """
        return {regname: register.value for regname, register in self.registers()}

    @classmethod
    def from_dict(cls, __mapping: Mapping[str, int], /) -> Self:
        """Create a new configuration object from persistent data.

        Args:
            __mapping (Mapping[str, int]): the data

        Returns:
            the new instance
        """
        return cls(**__mapping)

    def to_bytes(self) -> bytes:
        """Serialize the configuration object as bytes

        Returns:
            the content of the configuration object as bytes
        """
        address_register_mapping = {
            register.address: register for _, register in self.registers()
        }
        return b"".join(
            register.value.to_bytes(REGISTER_SIZE_BYTES, "big")
            if (register := address_register_mapping.get(address)) is not None
            else b"\x00\x00\x00\x00"
            for address in range(0, CONFIG_OBJECT_SIZE_BYTES, REGISTER_SIZE_BYTES)
        )

    @classmethod
    def from_bytes(cls, __data: bytes, /) -> Self:
        """Create a new configuration object from raw bytes

        Args:
            __data (bytes): the serialized configuration object

        Returns:
            the new instance
        """

        def _chunked(data: bytes) -> Iterator[int]:
            it = iter(data)
            while chunk := bytes(islice(it, REGISTER_SIZE_BYTES)):
                yield int.from_bytes(chunk, "big")

        new_instance = cls()
        address_register_mapping = {
            register.address: register for _, register in new_instance.registers()
        }

        for value, address in zip(_chunked(__data), count(step=REGISTER_SIZE_BYTES)):
            if (register := address_register_mapping.get(address)) is not None:
                register.value = value

        return new_instance


class ConfigurationObjectModel(BaseModel):
    @root_validator
    def remove_none_values(cls, values: Mapping[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in values.items() if v is not None}
