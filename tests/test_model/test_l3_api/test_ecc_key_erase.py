from typing import Any, Dict

import pytest
from _pytest.fixtures import SubRequest

from tvl.api.l3_api import TsL3EccKeyEraseCommand, TsL3EccKeyEraseResult
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
def test_erasing_ok(slot: int, host: Host, model: Tropic01Model):
    assert model.r_ecc_keys.slots[slot] is not None
    result = host.send_command(TsL3EccKeyEraseCommand(slot=slot))

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3EccKeyEraseResult)
    assert model.r_ecc_keys.slots[slot] is None


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10))
def test_no_key(host: Host, model: Tropic01Model, slot: int):
    assert model.r_ecc_keys.slots[slot] is None
    result = host.send_command(TsL3EccKeyEraseCommand(slot=slot))

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3EccKeyEraseResult)
    assert model.r_ecc_keys.slots[slot] is None


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.INVALID_INDICES, 10))
def test_invalid_slot(host: Host, model: Tropic01Model, slot: int):
    assert model.r_ecc_keys.slots[slot] is None
    result = host.send_command(TsL3EccKeyEraseCommand(slot=slot))

    assert result.result.value == L3ResultFieldEnum.UNAUTHORIZED
    assert model.r_ecc_keys.slots[slot] is None
