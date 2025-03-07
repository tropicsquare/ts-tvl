from enum import IntEnum
from functools import partial
from random import choice, getrandbits, randint
from typing import Callable, Dict, Optional, Tuple, Type, TypeVar, Union

from .datafield import AUTO, DataFieldInputData, Params
from .message import BaseMessage

M = TypeVar("M", bound=BaseMessage)


def getrandbytes(k: int, /) -> bytes:
    """Generate random bytes

    Args:
        k (int): number of bytes

    Returns:
        random bytes
    """
    if k == 0:
        return b""
    return getrandbits(k * 8).to_bytes(k, "big")


def get_random_datafield(__p: Params, /) -> bytes:
    """Generate random data that fit in a Datafield

    Args:
        __p (Params): parameters of the Datafield

    Returns:
        random data
    """
    return getrandbytes(__p.dtype.nb_bytes * randint(__p.min_size, __p.max_size))


def get_enum(__cls: Type[BaseMessage], __field_name: str, /) -> Optional[Type[IntEnum]]:
    """Get the enumeration class associated to a field inside a class

    Args:
        __cls (Type[BaseMessage]): The BaseMessage type the field belongs to
        __field_name (str): the field name

    Returns:
        the associated enumeration if it exists, `None` otherwise
    """
    return getattr(
        __cls, __field_name.replace("_", " ").title().replace(" ", "") + "Enum", None
    )


def one_of(__enum: Type[IntEnum], /) -> Callable[[], int]:
    """Randomly draw a random element from an integer enumeration

    Args:
        __enum (Type[IntEnum]): the enumeration to draw from

    Returns:
        an element of the enumeration
    """
    return lambda: choice(tuple(__enum))


def scrutinize(
    __cls: Type[BaseMessage], /
) -> Dict[str, Tuple[Callable[[], DataFieldInputData], bool]]:
    """Extract useful information about the fields of a BaseMessage class.

        The function returns a dictionary whose keys are the names of the
        field of the BaseMessage class and the values are tuples
        `<function for generating data; default value is AUTO>`

    Args:
        __cls (Type[BaseMessage]): the BaseMessage class to scrutinize

    Returns:
        information to generate data for the fields
    """
    info: Dict[str, Tuple[Callable[[], DataFieldInputData], bool]] = {}

    for field_name, _, params in __cls.specs():
        # Draw a randomly-chosen value from the field's enumeration
        if (enum := get_enum(__cls, field_name)) is not None:
            fn = one_of(enum)
        # Fill the field with random bytes
        else:
            fn = partial(get_random_datafield, params)
        info[field_name] = (fn, params.default is AUTO)
    return info


def randomize(
    __cls: Type[M],
    /,
    *,
    randomize_auto: bool = False,
    **kwargs: Union[DataFieldInputData, Callable[[], DataFieldInputData]],
) -> M:
    """Instantiate a BaseMessage with randomized content.

    Args:
        __cls (Type[M]):
            the BaseMessage class to instantiate
        randomize_auto (bool, optional):
            provide a random value to the fields whose default value is `AUTO`.
            Defaults to False.
        **kwargs (Union[DataFieldInputData, Callable[[], DataFieldInputData]]):
            user-defined values or callables that provide a value to a specific field.
            Have precedence over randomize_auto argument.

    Returns:
        an instance of the BaseMessage class
    """

    fields: Dict[str, Union[DataFieldInputData, Callable[[], DataFieldInputData]]] = {}

    for field_name, (fn, default_is_auto) in scrutinize(__cls).items():
        # Use user-defined argument
        if (user_arg := kwargs.get(field_name)) is not None:
            fields[field_name] = user_arg
        # Do not randomize fields whose default value is AUTO
        elif default_is_auto and not randomize_auto:
            continue
        # Use default randomize function
        else:
            fields[field_name] = fn

    return __cls(**{k: v() if callable(v) else v for k, v in fields.items()})
