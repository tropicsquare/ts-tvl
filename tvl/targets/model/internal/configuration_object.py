# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import contextlib
from typing import Any, Dict, Iterator, Mapping, Tuple

from pydantic import BaseModel, root_validator  # type: ignore
from typing_extensions import Self

CONFIG_OBJECT_SIZE_BYTES = 0x200
REGISTER_SIZE_BITS = 32
REGISTER_SIZE_BYTES = 32 // 8
NB_REGISTERS = CONFIG_OBJECT_SIZE_BYTES // REGISTER_SIZE_BYTES
REGISTER_RESET_VALUE = b"\xff" * REGISTER_SIZE_BYTES
REGISTER_MASK = 2**REGISTER_SIZE_BITS - 1
REGISTER_STR_NB_CHARS = REGISTER_SIZE_BITS // 4 + 2
ENDIANESS = "big"

# Whole Configuration Object address space could be accessed (no register need to be defined at given address)
CONFIGURATION_ACCESS_PRIVILEGES = range(0x000, 0x100, 0x4)
FUNCTIONALITY_ACCESS_PRIVILEGES = range(0x100, 0x200, 0x4)


class ConfigObjectError(Exception):
    pass


class AddressNotAlignedError(ConfigObjectError):
    pass


class AddressOutOfRangeError(ConfigObjectError):
    pass


class NoFreeSpaceError(ConfigObjectError):
    pass


class BitIndexOutOfBoundError(ConfigObjectError):
    pass


class ConfigObjectRegister:
    """Register contained in a configuration object"""

    def __init__(self, co: "ConfigurationObject", address: int) -> None:
        self.co = co
        self.address = address

    @property
    def value(self) -> int:
        return self.co.read(self.address)


class ConfigObjectField:
    """Register's field"""

    def __init__(self, offset: int, width: int) -> None:
        self.offset = offset
        self.mask = 2**width - 1

    def __get__(self, instance: ConfigObjectRegister, _) -> int:
        return instance.value >> self.offset & self.mask


class ConfigurationObject:
    """Chip configuration abstraction"""

    def __init__(self, **kwargs: int) -> None:
        self.data: bytearray
        self.erase()

        for regname, register in self.registers():
            with contextlib.suppress(KeyError):
                value = kwargs[regname]
                self.write(register.address, value, check=False)

    def registers(self) -> Iterator[Tuple[str, ConfigObjectRegister]]:
        """Go over the registers of the configuration object."""
        for key, value in self.__dict__.items():
            if isinstance(value, ConfigObjectRegister):
                yield key, value

    def __and__(self, __other: Any) -> Self:
        if not isinstance(__other, self.__class__):
            return NotImplemented

        new_instance = self.__class__()

        for address in (register.address for _, register in self.registers()):
            and_ = self.read(address) & __other.read(address)
            new_instance.write(address, and_)

        return new_instance

    def __eq__(self, __other: Any) -> bool:
        if __other is self:
            return True

        if not isinstance(__other, self.__class__):
            return NotImplemented

        return self.to_bytes() == __other.to_bytes()

    def __str__(self) -> str:
        registers = "; ".join(
            f"{regname}={register.value:#0{REGISTER_STR_NB_CHARS}x}"
            for regname, register in self.registers()
        )
        return f"{self.__class__.__name__}({registers})"

    @staticmethod
    def _check_address(address: int) -> None:
        if not 0 <= address < CONFIG_OBJECT_SIZE_BYTES:
            raise AddressOutOfRangeError("Address out of range")

        if address % REGISTER_SIZE_BYTES != 0:
            raise AddressNotAlignedError("Address should be word-aligned")

    def erase(self) -> None:
        """Erase the memory content."""
        self.data = bytearray(REGISTER_RESET_VALUE * NB_REGISTERS)

    def write(self, address: int, value: int, *, check: bool = True) -> None:
        """Write to the memory.

        Args:
            address (int): address to write the data
            value (int): data to write
            check (bool, optional): check the word is reset beforehand. Defaults to True.

        Raises:
            NoFreeSpaceError: (if check is enabled) register cannot be written
        """
        self._check_address(address)

        if check:
            current_value = bytes(self.data[address : address + REGISTER_SIZE_BYTES])
            if current_value != REGISTER_RESET_VALUE:
                raise NoFreeSpaceError("Register already written")

        self.data[address : address + REGISTER_SIZE_BYTES] = value.to_bytes(
            REGISTER_SIZE_BYTES, ENDIANESS
        )

    def write_bit(self, address: int, bit_index: int) -> None:
        """Write a bit from one to zero.

        Args:
            address (int): address of the word
            bit_index (int): index of the bit to flip

        Raises:
            BitIndexOutOfBoundError: bit is not reachable
        """
        current_value = self.read(address)

        if not 0 <= bit_index < REGISTER_SIZE_BITS:
            raise BitIndexOutOfBoundError(f"Bit index is out of bound: {bit_index}")

        masked_value = ~(2**bit_index) & REGISTER_MASK
        new_value = current_value & masked_value
        self.write(address, new_value, check=False)

    def read(self, address: int) -> int:
        """Read the memory.

        Args:
            address (int): address to read

        Returns:
            the word stored at the address
        """
        self._check_address(address)
        return int.from_bytes(
            self.data[address : address + REGISTER_SIZE_BYTES], ENDIANESS
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
            a new instance
        """
        return cls(**__mapping)

    def to_bytes(self) -> bytes:
        """Serialize the configuration object as bytes

        Returns:
            the content of the configuration object as bytes
        """
        return bytes(self.data)

    @classmethod
    def from_bytes(cls, __data: bytes, /) -> Self:
        """Create a new configuration object from raw bytes

        Args:
            __data (bytes): the serialized configuration object

        Returns:
            a new instance
        """
        new_instance = cls()
        new_instance.data = bytearray(__data)
        return new_instance


class ConfigurationObjectModel(BaseModel):
    @root_validator  # type: ignore
    def remove_none_values(cls, values: Mapping[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in values.items() if v is not None}
