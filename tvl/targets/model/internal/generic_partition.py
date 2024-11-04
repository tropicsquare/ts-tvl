# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from dataclasses import asdict, dataclass
from typing import Any, DefaultDict, Dict, Mapping, Type, TypeVar

from pydantic import BaseModel
from typing_extensions import Self


@dataclass
class BaseSlot:
    def to_dict(self) -> Dict[str, Any]:
        """Save the content of the slot in a dict.

        Returns:
            the content of the slot
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, __mapping: Mapping[str, Any], /) -> Self:
        """Create a new slot from a dict content.

        Args:
            __mapping (Mapping[str, Any]): the content of the slot

        Returns:
            a new slot
        """
        return cls(**__mapping)


T = TypeVar("T", bound=BaseSlot)


class GenericPartition(DefaultDict[int, T]):
    SLOT_TYPE: Type[T]

    def __init_subclass__(cls) -> None:
        # get the type provided as argument of the generic class
        cls.SLOT_TYPE = cls.__orig_bases__[0].__args__[0]  # type: ignore

    def __init__(self) -> None:
        super().__init__(self.SLOT_TYPE)

    def to_dict(self) -> Dict[int, Any]:
        """Save the content of the partition in a dict.

        Returns:
            the content of the partition
        """
        return {k: v.to_dict() for k, v in self.items()}

    @classmethod
    def from_dict(cls, __mapping: Mapping[int, Any], /) -> Self:
        """Create a new partition from a dict content.

        Args:
            __mapping (Mapping[str, Any]): the content of the partition

        Returns:
            a new partition
        """
        instance = cls()
        for k, v in __mapping.items():
            instance[k] = cls.SLOT_TYPE.from_dict(v)
        return instance


class GenericModel(BaseModel):
    def dict(self, **kwargs: Any) -> Dict[int, Any]:  # type: ignore
        return super().dict(**kwargs)["__root__"]
