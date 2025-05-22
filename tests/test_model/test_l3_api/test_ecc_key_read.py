from typing import Any, Dict

import pytest
from _pytest.fixtures import SubRequest

from tvl.api.l3_api import TsL3EccKeyReadCommand, TsL3EccKeyReadResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model

from ..utils import UtilsEcc, as_slow


@pytest.fixture()
def slot(model_configuration: Dict[str, Any], request: SubRequest):
    model_configuration.update(
        {"r_ecc_keys": {(val := request.param): UtilsEcc.get_valid_data()}}
    )
    yield val


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10), indirect=True)
def test_reading_ok(slot: int, host: Host, model: Tropic01Model):
    assert (before := model.r_ecc_keys.slots[slot]) is not None
    command = TsL3EccKeyReadCommand(
        slot=slot,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3EccKeyReadResult)
    assert result.curve.value == before.CURVE
    assert result.origin.value == (b := before.to_dict())["origin"]
    assert result.pub_key.to_bytes() == b["a"]
    assert model.r_ecc_keys.slots[slot] == before


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10))
def test_no_key(host: Host, model: Tropic01Model, slot: int):
    assert model.r_ecc_keys.slots[slot] is None
    command = TsL3EccKeyReadCommand(
        slot=slot,
    )
    result = host.send_command(command)

    assert result.result.value == TsL3EccKeyReadResult.ResultEnum.INVALID_KEY


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.INVALID_INDICES, 10))
def test_invalid_slot(host: Host, model: Tropic01Model, slot: int):
    assert model.r_ecc_keys.slots[slot] is None
    command = TsL3EccKeyReadCommand(
        slot=slot,
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.UNAUTHORIZED
    assert model.r_ecc_keys.slots[slot] is None
