import contextlib
import functools
import struct
from collections import ChainMap
from itertools import islice
from typing import Any, Callable, ClassVar, Dict, Iterator, List, Optional, Tuple, Type

from typing_extensions import (
    Annotated,
    Self,
    dataclass_transform,
    get_args,
    get_origin,
    get_type_hints,
)

from ..utils import iter_subclasses
from .datafield import DataField, Dtype, Params, U8Array, U8Scalar, datafield
from .endianness import endianness
from .exceptions import (
    FieldAlreadyExistsError,
    InsuficientDataLengthError,
    NegativeLengthError,
    NoValidSubclassError,
    ReservedFieldNameError,
    SubclassNotFoundError,
    UnsupportedFieldTypeError,
    UnsupportedTypeAnnotationError,
)

_RESERVED_FIELD_NAMES = {"data_field_bytes"}


def _get_specs(__cls: type, /) -> Iterator[Tuple[str, Type[DataField[Any]], Params]]:
    return (
        (name, *get_args(anns))
        for name, anns in get_type_hints(__cls, include_extras=True).items()
        if get_origin(anns) is Annotated
    )


@dataclass_transform(kw_only_default=True, field_specifiers=(datafield,))
class _MetaMessage(type):
    """
    Metaclass of the Message class.

    Make sure the field names are unique
    and add parameters to the DataField objects
    """

    def __new__(
        mcs,
        name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
        **kwargs: Any,
    ) -> "_MetaMessage":
        existing_fields = {n for base in bases for n, *_ in _get_specs(base)}

        annotations: Dict[str, Any] = namespace.get("__annotations__", {})

        for field_name, field_annot in annotations.items():
            if field_name in _RESERVED_FIELD_NAMES:
                raise ReservedFieldNameError(
                    f"Cannot add field '{field_name}': name reserved."
                )
            if field_name in existing_fields:
                raise FieldAlreadyExistsError(
                    f"Cannot add field '{field_name}': already exists."
                )

            if (origin := get_origin(field_annot)) is ClassVar:
                continue
            elif origin is not Annotated:
                raise UnsupportedTypeAnnotationError(
                    f"Only {ClassVar} and {Annotated} are supported; got {origin}"
                )

            tp, *params_args = get_args(field_annot)

            if not issubclass(tp, DataField):
                raise UnsupportedFieldTypeError(f"Field type {tp} not supported.")

            params = Params(**ChainMap(*params_args, namespace.pop(field_name, {})))

            annotations[field_name] = Annotated[tp, params]  # type: ignore

        return super().__new__(mcs, name, bases, namespace, **kwargs)


class BaseMessage(metaclass=_MetaMessage):
    @classmethod
    @functools.lru_cache
    def specs(cls) -> List[Tuple[str, Type[DataField[Any]], Params]]:
        """Go over the field specifications of the Message.

        Returns:
            the list of the field name, type and parameters
        """
        return sorted(_get_specs(cls), key=lambda x: x[2].priority)

    def __init__(self, **kwargs: Any) -> None:
        for name, type_, params in self.specs():
            value = kwargs.get(name, params.default)
            setattr(self, name, type_(value=value, params=params))

    def __eq__(self, __other: Any) -> bool:
        if __other is self:
            return True
        if isinstance(__other, BaseMessage):
            return __other.to_bytes() == self.to_bytes()
        return NotImplemented

    def __iter__(self) -> Iterator[Tuple[str, DataField[Any]]]:
        yield from self.__dict__.items()

    def __len__(self) -> int:
        return sum(len(field) for _, field in self)

    def __str__(self) -> str:
        values = ", ".join(f"{name}={field.hexstr()}" for name, field in self)
        return f"{self.__class__.__name__}{endianness.fmt}({values})"

    @property
    def data_field_bytes(self) -> bytes:
        """Returns the content of the DATA field of the message.

        Returns:
            the content of the DATA field
        """
        return b"".join(field.to_bytes() for _, field in self if field.params.is_data)

    def to_bytes(self) -> bytes:
        """Serialize a message to bytes

        Returns:
            the serialized content of the Message
        """
        return b"".join(field.to_bytes() for _, field in self)

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        /,
        *,
        fn: Optional[Callable[[Tuple[str, Type[DataField[Any]], Params]], bool]] = None,
    ) -> Self:
        """Deserialize a Message instance from bytes representation.

        Args:
            data (bytes): bytes representation of a message
            fn (Optional[Tuple[Callable[[str, Type[DataField[Any]], Params]], bool]], optional):
                only the fields for which fn returns True are going to be deserialized,
                the others will be included with their default value

        Returns:
            Message instance
        """
        fmt_dict: Dict[str, Tuple[int, Dtype]] = {}
        varsize_field_name: Optional[str] = None

        # Collect the minimum size and the datatype of each field
        for name, _, params in filter(fn, cls.specs()):
            fmt_dict[name] = (params.min_size, params.dtype)

            # If a field has a variable size, mark it and perform a second pass
            if params.has_variable_size():
                if varsize_field_name is not None:
                    raise RuntimeError(
                        "Only one field is allowed to have a variable size"
                    )
                varsize_field_name = name

        # One field was found that has a variable size, compute its format now
        if varsize_field_name is not None:
            min_size, dtype = fmt_dict[varsize_field_name]

            known_len = sum(
                min_size * dtype.nb_bytes
                for name, (min_size, dtype) in fmt_dict.items()
                if name != varsize_field_name
            )
            nb_bytes_left = len(data) - known_len
            min_nb_bytes = min_size * dtype.nb_bytes

            if nb_bytes_left < min_nb_bytes:
                raise InsuficientDataLengthError(
                    f"{nb_bytes_left} bytes left; "
                    f"field '{varsize_field_name}' requires at least {min_nb_bytes}."
                )
            fmt_dict[varsize_field_name] = (nb_bytes_left // dtype.nb_bytes, dtype)

        # Unpack each field and instantiate a new instance of the class
        fmt = endianness.fmt + "".join(f"{sz}{dt}" for sz, dt in fmt_dict.values())
        it = iter(struct.unpack(fmt, data))

        return cls(**{name: list(islice(it, sz)) for name, (sz, _) in fmt_dict.items()})


class Message(BaseMessage):
    ID: ClassVar[int]
    """id of the class"""

    def __init_subclass__(cls, *, id: Optional[int] = None) -> None:
        """Associate an id to the subclasses of Message.

        Args:
            id (int, optional): ID associated to the subclass.
                Defaults to None.
        """
        if id is not None:
            cls.ID = id

    @classmethod
    def find_subclasses(cls, id: int) -> List[Type[Self]]:
        """Find all the subclasses with the specified id."""
        return [s for s in iter_subclasses(cls) if getattr(s, "ID", None) == id]

    @classmethod
    def instantiate_subclass(cls, id: int, data: bytes) -> Self:
        """Find a subclass with the specified id and deserialize the data
        according to its structure.

        Args:
            id (int): the ID associated to the message type
            data (bytes): the data to deserialize

        Raises:
            NoValidSubclassError: a subclass was found but the data could
            not be deserialized
            SubclassNotFoundError: no subclass associated to the id was found

        Returns:
            an instance of a subclass with the deserialized data
        """
        if not (subclasses := cls.find_subclasses(id)):
            raise SubclassNotFoundError(
                f"No subclass of {cls.__name__} with {id=:#x} was found."
            )

        for subclass in subclasses:
            with contextlib.suppress(Exception):
                return subclass.from_bytes(data)

        raise NoValidSubclassError(
            f"No valid subclass of {cls.__name__} with {id=:#x}."
        )

    @classmethod
    def with_data_length(cls, length: int) -> Type[Self]:
        """Create a new subclass having a field 'data' with a specific length.

        Returns:
            the new subclass
        """
        if length < 0:
            raise NegativeLengthError(f"length should be positive: {length}.")

        if length >= 1:
            default_data_field_name = "data"

            if length > 1:
                namespace = {  # type: ignore
                    "__annotations__": {default_data_field_name: U8Array},
                    default_data_field_name: datafield(size=length),
                }
            else:
                namespace = {
                    "__annotations__": {default_data_field_name: U8Scalar},
                }
        else:
            namespace = {}

        return type(f"Default{cls.__name__}", (cls,), namespace, id=-1)  # type: ignore

    @classmethod
    def with_length(cls, length: int) -> Type[Self]:
        """Create a new subclass having a specific total length.

        Returns:
            the new subclass
        """
        return cls.with_data_length(length - len(cls.with_data_length(0)()))
