# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import functools
import logging
from collections import defaultdict
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypeVar,
    cast,
)

from typing_extensions import Self


class HasLogger(Protocol):
    logger: logging.Logger


F = TypeVar("F", bound=Callable[..., Any])

__api_base__ = "__api_base__"
__api_overload__ = "__api_overload__"


class MetaModel(type):
    """
    Metaclass for the TROPIC01 model

    Allows method to be defined as base methods in the api and overrides
    these latter.This class wraps the `singledispatchmethod` mechanism.
    """

    def __new__(
        cls, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]
    ) -> Self:
        new_cls = super().__new__(cls, name, bases, namespace)

        api_bases: Dict[str, "functools.singledispatchmethod[Any]"] = {}
        api_over: DefaultDict[str, Set[str]] = defaultdict(set)
        api_types: Dict[str, Optional[Tuple[type, ...]]] = {}

        # look for base methods and overloads
        for _cls in reversed(new_cls.__mro__[:-1]):
            for attr_name, attr in _cls.__dict__.items():
                # add base method
                if (_id := getattr(attr, __api_base__, None)) is not None:
                    api_bases[_id] = attr
                # add overload method
                elif (tp := getattr(attr, __api_overload__, None)) is not None:
                    _id, _types = tp
                    api_over[_id].add(attr_name)
                    # save associated types
                    api_types[attr_name] = _types

        # register the overloads
        for _id, _base in api_bases.items():
            for over_name in api_over[_id]:
                over = getattr(new_cls, over_name)
                if (_types := api_types[over_name]) is not None:
                    # register with types if passed
                    registered = over
                    for _type in _types:
                        registered = _base.register(_type)(registered)
                else:
                    # register with the annotated types
                    registered = _base.register(over)
                decorated = _log_processing(registered)
                # assign new method to class
                setattr(new_cls, over_name, decorated)

        return new_cls


def base(__id: str, /) -> Callable[[F], F]:
    """Define the decorated method as base method of the api.

    Args:
        __id (str): the identifier of the method.

    Returns:
        the same method, marked as base.
    """

    def _base(method: F) -> F:
        _method = functools.singledispatchmethod(method)
        setattr(_method, __api_base__, __id)
        return cast(F, _method)

    return _base


def api(__id: str, __dt: Optional[Tuple[type, ...]] = None, /) -> Callable[[F], F]:
    """Define the decorated method as overloading the associated base method.

    Args:
        __id (str): the identifier of the associated base method.
        dt (type, optional): explicitly force the type if needed.

    Returns:
        the same method, overloading the base with the same identifier.
    """

    def _api(method: F) -> F:
        setattr(method, __api_overload__, (__id, __dt))
        return method

    return _api


def _log_processing(method: F) -> F:
    """Log the call to the method."""

    @functools.wraps(method)
    def __log_processing(self: HasLogger, request: Any) -> Any:
        self.logger.info((_line := f"-------- {method.__qualname__} --------"))
        try:
            return method(self, request)
        except Exception as exc:
            self.logger.info(exc)
            raise
        finally:
            self.logger.info("-" * len(_line))

    return cast(F, __log_processing)
