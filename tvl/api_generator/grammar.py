# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from collections import Counter
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Extra, Field, root_validator


class InoutTypeEnum(str, Enum):
    U8 = "u8"
    U16 = "u16"
    U32 = "u32"
    U64 = "u64"

    @property
    def nb_bytes(self) -> int:
        return int(self.value[1:]) // 8

    def __str__(self) -> str:
        return self.value


class _BaseModel(BaseModel):
    class Config:
        extra = Extra.ignore
        frozen = True


class SimpleValueModel(_BaseModel):
    name: str
    value: int
    description: Optional[str]


class ChoiceModel(_BaseModel):
    choices: List[SimpleValueModel]


class InoutModel(_BaseModel):
    name: str
    description: Optional[str]
    description_long: Optional[str]
    type: InoutTypeEnum
    size: Optional[int]
    min_size: Optional[int]
    max_size: Optional[int]
    choices: Optional[List[SimpleValueModel]]

    @root_validator
    def check_size_fields(cls, values: Dict[str, Optional[int]]) -> Dict[str, Any]:
        # 'size' can be specifed only if 'min_size' and 'max_size' are not
        if values["size"] is None:
            if None in (values["min_size"], values["max_size"]):
                raise ValueError
        elif None not in (values["min_size"], values["max_size"]):
            raise ValueError
        return values


class FunctionModel(_BaseModel):
    input: Optional[List[InoutModel]]
    output: Optional[List[InoutModel]]


class CommandModel(_BaseModel):
    name: str
    description: str
    description_long: Optional[str]
    message_id: int
    result: Optional[ChoiceModel]
    function: FunctionModel


class DefineModel(SimpleValueModel):
    pass


class InputFileModel(_BaseModel):
    commands: List[CommandModel]
    defines: List[DefineModel] = Field(default_factory=list)

    @root_validator
    def forbid_message_id_duplicates(
        cls, values: Dict[str, List[CommandModel]]
    ) -> Dict[str, Any]:
        counter = Counter(cfg.message_id for cfg in values["commands"])
        if duplicates := [_id for _id, cnt in counter.items() if cnt > 1]:
            raise ValueError(f"Some message ids are duplicated! {duplicates}")
        return values
