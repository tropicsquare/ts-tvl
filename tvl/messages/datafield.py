# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import struct
from dataclasses import InitVar, dataclass
from enum import Enum, IntEnum, auto
from functools import singledispatch
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    List,
    Literal,
    Optional,
    TypedDict,
    TypeVar,
    Union,
)

from typing_extensions import Annotated, Unpack

from .endianness import endianness
from .exceptions import DataValueError, ListTooLongError, TypeNotSupportedError

T = TypeVar("T")

DataFieldInputData = Union[int, List[int], bytes]


class ParamError(Exception):
    pass


class _AUTO(IntEnum):
    AUTO = auto()

    def __str__(self) -> str:
        return self.name


AUTO = _AUTO.AUTO
"""AUTO value for specific fields. Conversion of these must be implemented."""


class Dtype(str, Enum):
    """Integer types and their format for conversion to bytes"""

    UINT8 = "B"
    UINT16 = "H"
    UINT32 = "I"
    UINT64 = "Q"

    @property
    def nb_bytes(self) -> int:
        return struct.calcsize(self.value)


@dataclass(frozen=True)
class Params:
    """Define the parameters of a DataField."""

    dtype: Dtype
    size: InitVar[Optional[int]] = None
    min_size: int = 1
    max_size: int = 1
    priority: int = 0
    is_data: bool = True
    default: DataFieldInputData = 0

    def __post_init__(self, size: Optional[int]):
        if size is not None:
            object.__setattr__(self, "min_size", size)
            object.__setattr__(self, "max_size", size)
        if self.min_size < 0:
            raise ParamError("Min size should be at least 0.")
        if self.max_size < 1:
            raise ParamError("Max size should be at least 1.")
        if self.max_size < self.min_size:
            raise ParamError("Max size should be greater than or equal to min size.")

    def has_variable_size(self) -> bool:
        """A field can contain a variable number of elements."""
        return self.min_size != self.max_size


class _ParamsFnArgs(TypedDict, total=False):
    dtype: Dtype
    size: int
    min_size: int
    max_size: int
    priority: int
    is_data: bool


def params(**kwargs: Unpack[_ParamsFnArgs]):
    """Define the parameters of a DataField.

    Args:
        dtype (Dtype): type of the elements in the DataField
        size (int): number of elements; overrides 'min_size' and 'max_size'
        min_size (int): minimum number of elements
        max_size (int): maximum number of elements
        priority (int): order of the DataField during the serialization;
            the lesser the number, the higher the priority
        is_data (bool): if True, is part of the DATA field of the Message
    """
    return kwargs


@singledispatch
def _format_to_list(value: Any, instance: "DataField[Any]") -> List[int]:
    raise TypeNotSupportedError(f"Type {type(value)} not supported.")


@_format_to_list.register(int)
def _(value: int, instance: "DataField[Any]") -> List[int]:
    return [value]


@_format_to_list.register(bytes)
def _(value: bytes, instance: "DataField[Any]") -> List[int]:
    try:
        return list(struct.unpack(f"{endianness.fmt}{instance.params.dtype}", value))
    except struct.error:
        return list(struct.unpack(f"{endianness.fmt}{len(value)}{Dtype.UINT8}", value))


@_format_to_list.register(list)
def _(value: List[int], instance: "DataField[Any]") -> List[int]:
    return value


class ValueDescriptor(Generic[T]):
    def __set_name__(self, _, name: str) -> None:
        self.name = f"_{name}"

    def __init__(self, getter_fn: Callable[[List[int]], T]) -> None:
        self.getter_fn = getter_fn

    def __set__(self, instance: "DataField[Any]", value: DataFieldInputData) -> None:
        """Sets the value of a DataField

        Args:
            instance (DataField[Any]): field of which the value wll be written
            value (DataFieldInputData): the value to write

        Raises:
            TypeNotSupportedError: cannot process the type of value
            ListTooLongError: the value array contains too many elements
        """

        if value is AUTO:
            return setattr(instance, self.name, value)

        value = _format_to_list(value, instance)

        # check list length
        if (length := len(value)) > instance.params.max_size:
            raise ListTooLongError(f"{length=} > {instance.params.max_size}.")

        # pad with zeroes
        if instance.params.has_variable_size():
            min_length = instance.params.min_size
        else:
            min_length = instance.params.max_size
        if (padding_length := min_length - len(value)) > 0:
            value.extend([0] * padding_length)

        setattr(instance, self.name, value)

    def __get__(self, instance: "DataField[Any]", _) -> T:
        """Gets the value of a DataField

        Args:
            instance (DataField[Any]): the field from which read the value

        Returns:
            the value of the field
        """
        if (value := getattr(instance, self.name)) is AUTO:
            return value  # type: ignore
        return self.getter_fn(value)


class DataField(Generic[T]):
    """Base class for defining the fields of a message"""

    value: ValueDescriptor[T]

    def __init__(self, value: DataFieldInputData, params: Params) -> None:
        self._value: Union[List[int], Literal[AUTO]]
        self.params = params
        self.value = value

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}" f"(value={self.value}, params={self.params})"
        )

    def __len__(self) -> int:
        if self._value is AUTO:
            return self.params.min_size * self.params.dtype.nb_bytes
        return len(self._value) * self.params.dtype.nb_bytes

    if TYPE_CHECKING:
        # dummy setter for IDE during message initialization
        def __set__(self, instance: object, value: DataFieldInputData) -> None:
            ...

    def to_bytes(self) -> bytes:
        assert isinstance(self._value, list), f"'{self._value}' is not a list"
        try:
            return struct.pack(
                f"{endianness.fmt}{len(self._value)}{self.params.dtype}",
                *self._value,
            )
        except struct.error as exc:
            raise DataValueError(f"Wrong value={self._value}: {exc}") from None

    def hexstr(self) -> str:
        """Hexadecimal representation"""
        if (value := self.value) is AUTO:
            return str(value)
        return self._hexstr()

    def _hexstr(self) -> str:
        """Hexadecimal representation of the actual type; override in child"""
        raise NotImplementedError("TODO")


class ScalarDataField(DataField[int]):
    value = ValueDescriptor(getter_fn=lambda x: x[0])

    def _hexstr(self) -> str:
        nb_chars = self.params.dtype.nb_bytes * 2
        return f"{self.value:0{nb_chars}x}"


class ArrayDataField(DataField[List[int]]):
    value = ValueDescriptor(getter_fn=lambda x: x)

    def _hexstr(self) -> str:
        nb_chars = self.params.dtype.nb_bytes * 2
        return f"[{', '.join(f'{x:0{nb_chars}x}' for x in self.value)}]"


U8Scalar = Annotated[ScalarDataField, params(dtype=Dtype.UINT8)]
"""Unsigned char"""

U16Scalar = Annotated[ScalarDataField, params(dtype=Dtype.UINT16)]
"""Unsigned short"""

U32Scalar = Annotated[ScalarDataField, params(dtype=Dtype.UINT32)]
"""Unsigned int"""

U64Scalar = Annotated[ScalarDataField, params(dtype=Dtype.UINT64)]
"""Unsigned long"""


class U8Array(ArrayDataField):
    """Array of unsigned chars"""

    def __class_getitem__(cls, param: _ParamsFnArgs):
        return Annotated[cls.__base__, params(dtype=Dtype.UINT8), param]  # type: ignore


class U16Array(ArrayDataField):
    """Array of unsigned shorts"""

    def __class_getitem__(cls, param: _ParamsFnArgs):
        return Annotated[cls.__base__, params(dtype=Dtype.UINT16), param]  # type: ignore


class U32Array(ArrayDataField):
    """Array of unsigned ints"""

    def __class_getitem__(cls, param: _ParamsFnArgs):
        return Annotated[cls.__base__, params(dtype=Dtype.UINT32), param]  # type: ignore


class U64Array(ArrayDataField):
    """Array of unsigned longs"""

    def __class_getitem__(cls, param: _ParamsFnArgs):
        return Annotated[cls.__base__, params(dtype=Dtype.UINT64), param]  # type: ignore
