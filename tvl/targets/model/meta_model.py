import logging
from collections import defaultdict
from functools import reduce, singledispatchmethod, wraps
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    cast,
)


class HasLogger(Protocol):
    logger: logging.Logger


F = TypeVar("F", bound=Callable[..., Any])

__api_base__ = "__api_base__"
__api_overload__ = "__api_overload__"


class MetaModel:
    """
    Base class for the TROPIC01 model

    Allows methods to be defined as base methods in the api and overloads
    these latter. Uses the `singledispatchmethod` mechanism.
    """

    def __init_subclass__(cls) -> None:
        base_fns: Dict[str, "singledispatchmethod[Any]"] = {}
        overs: DefaultDict[
            str, List[Tuple[str, Optional[Tuple[type, ...]]]]
        ] = defaultdict(list)

        for cls_ in reversed(cls.__mro__[:-2]):
            for attr_name, attr in cls_.__dict__.items():
                # collect the base methods
                if (id_ := getattr(attr, __api_base__, None)) is not None:
                    base_fns[id_] = attr
                # collect the overloads and their associated types
                elif (tp := getattr(attr, __api_overload__, None)) is not None:
                    id_, types = tp
                    overs[id_].append((attr_name, types))

        # register the overloads of the base methods
        for id_, base_fn in base_fns.items():
            for over_name, types in overs[id_]:
                setattr(
                    cls,
                    over_name,
                    _log(_register(base_fn, getattr(cls, over_name), types)),
                )


def base(__id: str, /) -> Callable[[F], F]:
    """Define the decorated method as base method of the api.

    Args:
        __id (str): the identifier of the method.

    Returns:
        the same method, marked as base.
    """

    def _base(method: F) -> F:
        _method = singledispatchmethod(method)
        setattr(_method, __api_base__, __id)
        return cast(F, _method)

    return _base


def api(__id: str, __dt: Optional[Tuple[type, ...]] = None, /) -> Callable[[F], F]:
    """Define the decorated method as overloading the associated base method.

    Args:
        __id (str): the identifier of the associated base method.
        __dt (type, optional): explicitly force the type if needed.

    Returns:
        the same method, overloading the base with the same identifier.
    """

    def _api(method: F) -> F:
        setattr(method, __api_overload__, (__id, __dt))
        return method

    return _api


def _register(
    base: "singledispatchmethod[Any]",
    over: Callable[..., Any],
    types: Optional[Tuple[type, ...]] = None,
) -> Callable[..., Any]:
    """Register an overload of the base method with the specified types."""
    if types is None:
        # register with the annotated types
        return base.register(over)

    # register with specified types
    return reduce(lambda o, ty: base.register(ty)(o), types, over)


def _log(method: F) -> F:
    """Log the call to the method."""

    @wraps(method)
    def __log_processing(self: HasLogger, request: Any) -> Any:
        self.logger.debug(f"Executing {method.__qualname__}")
        try:
            return method(self, request)
        except Exception as exc:
            self.logger.info(exc)
            raise
        finally:
            self.logger.debug(f"Done executing {method.__qualname__}")

    return cast(F, __log_processing)
