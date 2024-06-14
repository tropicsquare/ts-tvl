# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
from typing import Any, Dict

import pytest
from _pytest.fixtures import SubRequest

from tvl.api.l3_api import TsL3EccKeyStoreCommand, TsL3EccKeyStoreResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.internal.ecc_keys import KEY_SIZE
from tvl.targets.model.tropic01_model import Tropic01Model

from ..utils import UtilsEcc, as_slow, one_of, one_outside


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10))
def test_storing_ok(host: Host, model: Tropic01Model, slot: int):
    assert model.r_ecc_keys.slots[slot] is None
    command = TsL3EccKeyStoreCommand(
        slot=slot,
        curve=one_of(TsL3EccKeyStoreCommand.CurveEnum),
        k=os.urandom(KEY_SIZE),
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3EccKeyStoreResult)
    assert model.r_ecc_keys.slots[slot] is not None


@pytest.fixture()
def slot(model_configuration: Dict[str, Any], request: SubRequest):
    model_configuration.update(
        {"r_ecc_keys": {(val := request.param): UtilsEcc.get_valid_data()}}
    )
    yield val


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10), indirect=True)
def test_key_already_exists(slot: int, host: Host, model: Tropic01Model):
    assert (before := model.r_ecc_keys.slots[slot]) is not None
    command = TsL3EccKeyStoreCommand(
        slot=slot,
        curve=one_of(TsL3EccKeyStoreCommand.CurveEnum),
        k=os.urandom(KEY_SIZE),
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
    assert isinstance(result, TsL3EccKeyStoreResult)
    assert model.r_ecc_keys.slots[slot] == before


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10))
def test_invalid_curve(host: Host, model: Tropic01Model, slot: int):
    assert model.r_ecc_keys.slots[slot] is None
    command = TsL3EccKeyStoreCommand(
        slot=slot,
        curve=one_outside(TsL3EccKeyStoreCommand.CurveEnum),
        k=os.urandom(KEY_SIZE),
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
    assert isinstance(result, TsL3EccKeyStoreResult)
    assert model.r_ecc_keys.slots[slot] is None


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.INVALID_INDICES, 10))
def test_invalid_slot(host: Host, model: Tropic01Model, slot: int):
    assert model.r_ecc_keys.slots[slot] is None
    command = TsL3EccKeyStoreCommand(
        slot=slot,
        curve=one_of(TsL3EccKeyStoreCommand.CurveEnum),
        k=os.urandom(KEY_SIZE),
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
    assert model.r_ecc_keys.slots[slot] is None
