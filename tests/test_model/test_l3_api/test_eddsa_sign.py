from typing import Any, Dict

import pytest
from _pytest.fixtures import SubRequest

from tvl.api.l3_api import TsL3EddsaSignCommand, TsL3EddsaSignResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.messages.randomize import randomize

from ..utils import UtilsEcc, as_slow


@pytest.fixture()
def slot(model_configuration: Dict[str, Any], request: SubRequest):
    model_configuration.update(
        {"r_ecc_keys": {(val := request.param): UtilsEcc.get_eddsa_key()}}
    )
    yield val


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10), indirect=True)
def test_eddsa_signature_ok(slot: int, host: Host):
    command = randomize(TsL3EddsaSignCommand, slot=slot)
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3EddsaSignResult)
    # TODO implement result checking against reference implementation


# TODO diff between no key and curve mismatch
@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10))
def test_no_key_and_bad_curve(host: Host, slot: int):
    command = randomize(TsL3EddsaSignCommand, slot=slot)
    result = host.send_command(command)

    assert result.result.value == TsL3EddsaSignResult.ResultEnum.INVALID_KEY
    assert not isinstance(result, TsL3EddsaSignResult)


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.INVALID_INDICES, 10))
def test_invalid_slot(host: Host, slot: int):
    command = randomize(TsL3EddsaSignCommand, slot=slot)
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.UNAUTHORIZED
