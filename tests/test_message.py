# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import importlib
from typing import Any, ContextManager, Type, Union

from tvl.messages import l2_messages

importlib.reload(l2_messages)

from contextlib import nullcontext

import pytest

from tvl.messages.datafield import AUTO, U16Scalar, U32Array, U64Scalar, params
from tvl.messages.exceptions import (
    DataValueError,
    FieldAlreadyExistsError,
    ListTooLongError,
    NegativeLengthError,
    NoValidSubclassError,
    ReservedFieldNameError,
    SubclassNotFoundError,
    TypeNotSupportedError,
    UnauthorizedInstantiationError,
)
from tvl.messages.l2_messages import L2Request
from tvl.messages.l3_messages import L3Command


class RequestTest1(L2Request, id=0x12):
    f1: U16Scalar = 0  # type: ignore
    f2: U32Array[params(size=3)] = 0  # type: ignore


class RequestTest2(L2Request, id=0x13):
    f1: U16Scalar


class ErrorRequest(L2Request):
    pass


class CommandTest(L3Command, id=0x12):
    f1: U64Scalar


class ErrorCommand(L3Command):
    pass


@pytest.mark.parametrize(
    "field_name, context",
    [
        pytest.param("f3", nullcontext(), id="ok"),
        pytest.param(
            "f1",
            pytest.raises(FieldAlreadyExistsError),
            id="already-exists-error",
        ),
        pytest.param(
            "data_field_bytes",
            pytest.raises(ReservedFieldNameError),
            id="reserved-name-error",
        ),
    ],
)
def test_creation(field_name: str, context: ContextManager[Any]):
    with context:
        type(
            "RequestTest3",
            (RequestTest1,),
            {
                "__annotations__": {field_name: U16Scalar},
            },
        )


@pytest.mark.parametrize(
    "to_instantiate, context",
    [
        pytest.param(RequestTest1, nullcontext(), id="ok"),
        pytest.param(
            ErrorRequest,
            pytest.raises(UnauthorizedInstantiationError),
            id="error",
        ),
        pytest.param(
            ErrorCommand,
            pytest.raises(UnauthorizedInstantiationError),
            id="error",
        ),
    ],
)
def test_instantiation(to_instantiate: type, context: ContextManager[Any]):
    with context:
        to_instantiate()


def test_subclasses():
    request = RequestTest1()
    request_bytes = request.to_bytes()
    assert isinstance(
        L2Request.instantiate_subclass(RequestTest1.ID, request_bytes),
        RequestTest1,
    )
    with pytest.raises(SubclassNotFoundError):
        L2Request.instantiate_subclass(0xFE, request_bytes)

    with pytest.raises(NoValidSubclassError):
        L2Request.instantiate_subclass(RequestTest1.ID, b"")

    with pytest.raises(NegativeLengthError):
        RequestTest1.with_length(0)

    empty_len = len(RequestTest1.with_data_length(0)())
    assert empty_len == len(RequestTest1())
    assert len(RequestTest1.with_data_length((dl := 0))()) == empty_len + dl
    assert len(RequestTest1.with_data_length((dl := 1))()) == empty_len + dl
    assert len(RequestTest1.with_data_length((dl := 2))()) == empty_len + dl


def test_message():
    request = RequestTest1()
    assert request.has_valid_id()

    request.id.value = [v := 0]
    assert request.id.value == v
    request.id.value = (v := 1)
    assert request.id.value == v

    with pytest.raises(ListTooLongError):
        request.id.value = [12, 34]
    with pytest.raises(DataValueError):
        request.id.value = [1.2]  # type: ignore
        request.id.to_bytes()
    with pytest.raises(TypeNotSupportedError):
        request.id.value = 1.2  # type: ignore

    assert not request.has_valid_id()

    request = RequestTest1(f1=(v := 0x99))
    assert request.f1.value == v

    request.f1.value = b"\x12\x34"
    assert request.f1.value == 0x3412

    request.f1.value = b"12"
    assert request.f1.value == ord("1") + (ord("2") << 8)

    assert request.crc.value is AUTO
    assert request.has_valid_crc()

    request.crc.value = 56
    assert not request.has_valid_crc()
    request.update_crc()
    assert request.has_valid_crc()

    request.id.value = AUTO

    _request = RequestTest1.from_bytes(request.to_bytes())
    assert _request.id.value == _request.ID
    assert _request.has_valid_id()


@pytest.mark.parametrize(
    "message_type",
    [
        pytest.param(RequestTest1, id="L2"),
        pytest.param(CommandTest, id="L3"),
    ],
)
def test_id(message_type: Union[Type[L2Request], Type[L3Command]]):
    message = message_type()
    assert message.has_valid_id()
    _message = message_type.from_bytes(message.to_bytes())
    assert _message.has_valid_id()


def test_equalities():
    assert RequestTest1(f1=(v := 0x99)) != RequestTest2(f1=v)

    assert RequestTest1(id=(h := 1)) != RequestTest1(id=h + 1)
    assert RequestTest1(length=(l := 1)) != RequestTest1(length=l + 1)
    assert RequestTest1(crc=(c := 0x1234)) != RequestTest1(crc=c + 1)

    assert RequestTest1() == RequestTest1()
    assert RequestTest1(id=(h := 1)) == RequestTest1(id=h)
    assert RequestTest1(length=(l := 1)) == RequestTest1(length=l)
    assert RequestTest1(crc=(c := 0x1234)) == RequestTest1(crc=c)

    assert (same := RequestTest1(f1=0x99, crc=0x1234)) == same

    assert RequestTest1() != "dummy"
