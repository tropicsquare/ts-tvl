# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
from typing import Any, Dict

import pytest
from _pytest.fixtures import SubRequest

from tvl.api.l3_api import TsL3EcdsaSignCommand, TsL3EcdsaSignResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host

from ..utils import UtilsEcc


def _get_msg_hash() -> bytes:
    return os.urandom(32)


@pytest.fixture()
def slot(model_configuration: Dict[str, Any], request: SubRequest):
    model_configuration.update(
        {"r_ecc_keys": {(val := request.param): UtilsEcc.get_ecdsa_key()}}
    )
    yield val


@pytest.mark.parametrize("slot", UtilsEcc.VALID_INDICES, indirect=True)
def test_ecdsa_signature_ok(slot: int, host: Host):
    command = TsL3EcdsaSignCommand(
        slot=slot,
        padding=b"",
        msg_hash=_get_msg_hash(),
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3EcdsaSignResult)
    # TODO implement result checking against reference implementation


# TODO diff between no key and curve mismatch
@pytest.mark.parametrize("slot", UtilsEcc.VALID_INDICES)
def test_no_key_and_bad_curve(host: Host, slot: int):
    command = TsL3EcdsaSignCommand(
        slot=slot,
        padding=b"",
        msg_hash=_get_msg_hash(),
    )
    result = host.send_command(command)

    assert result.result.value == TsL3EcdsaSignResult.ResultEnum.INVALID_KEY
    assert not isinstance(result, TsL3EcdsaSignResult)


# TODO implement
@pytest.mark.skip(reason="mock failed signature")
@pytest.mark.parametrize("slot", UtilsEcc.VALID_INDICES)
def test_signature_failed(host: Host, slot: int):
    command = TsL3EcdsaSignCommand(
        slot=slot,
        padding=b"",
        msg_hash=_get_msg_hash(),
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
    assert isinstance(result, TsL3EcdsaSignResult)


@pytest.mark.parametrize("slot", UtilsEcc.INVALID_INDICES)
def test_invalid_slot(host: Host, slot: int):
    command = TsL3EcdsaSignCommand(
        slot=slot,
        padding=b"",
        msg_hash=_get_msg_hash(),
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
