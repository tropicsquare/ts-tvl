from typing import Any, Dict

import pytest
from _pytest.fixtures import SubRequest


from tvl.api.l3_api import TsL3EddsaVerifyCommand, TsL3EddsaVerifyResult, TsL3EddsaSignCommand, TsL3EddsaSignResult
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

@pytest.fixture()
def unauthorized_slot(model_configuration: Dict[str, Any], request: SubRequest):
    val = request.param
    model_configuration.update(
        {"r_ecc_keys": {val: UtilsEcc.get_eddsa_key()}}
    )
    model_configuration.update(
        {"i_config": {"cfg_uap_eddsa_verify": 0x00000000}}  # Disable ECDSA verify for this slot
    )
    yield val

@pytest.fixture()
def sign_command(slot: int) -> TsL3EddsaSignCommand:
    return randomize(TsL3EddsaSignCommand, slot=slot)

@pytest.fixture()
def sign_result(host: Host, sign_command: TsL3EddsaSignCommand) -> TsL3EddsaSignResult:
    # Send the sign command to the host and return the result
    sign_result = host.send_command(sign_command)
    assert isinstance(sign_result, TsL3EddsaSignResult)
    return sign_result

@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10), indirect=True)
def test_eddsa_verify_ok(host: Host, sign_command: TsL3EddsaSignCommand, sign_result: TsL3EddsaSignResult):
    command = TsL3EddsaVerifyCommand(
        slot=sign_command.slot.value,
        msg=sign_command.msg.value,
        r=sign_result.r.value,
        s=sign_result.s.value
    )
    result = host.send_command(command)
    
    assert isinstance(result, TsL3EddsaVerifyResult)
    assert result.result.value == L3ResultFieldEnum.OK

@pytest.mark.parametrize("unauthorized_slot", as_slow(UtilsEcc.VALID_INDICES, 10), indirect=True)
def test_eddsa_verify_unauthorized_slot(unauthorized_slot: int, host: Host):
    sign_command = randomize(TsL3EddsaSignCommand, slot=unauthorized_slot)
    sign_result = host.send_command(sign_command)
    
    assert isinstance(sign_result, TsL3EddsaSignResult)

    command = TsL3EddsaVerifyCommand(
        slot=sign_command.slot.value,
        msg=sign_command.msg.value,
        r=sign_result.r.value,
        s=sign_result.s.value
    )
    result = host.send_command(command)
    
    assert isinstance(result, TsL3EddsaVerifyResult)
    assert result.result.value == L3ResultFieldEnum.UNAUTHORIZED

@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10), indirect=True)
@pytest.mark.parametrize("r,s", [(None, b"\x00" * 32), (b"\x01" * 32, None)])
def test_eddsa_verify_fail_wrong_signature(r: bytes, s: bytes, sign_command: TsL3EddsaSignCommand, sign_result: TsL3EddsaSignResult, host: Host):
    command = TsL3EddsaVerifyCommand(
        slot=sign_command.slot.value, 
        msg=sign_command.msg.value,
        r=r or sign_result.r.value,
        s=s or sign_result.s.value
    )
    result = host.send_command(command)
    
    assert isinstance(result, TsL3EddsaVerifyResult)
    assert result.result.value == L3ResultFieldEnum.FAIL

@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10), indirect=True)
@pytest.mark.parametrize("msg", [b"", b"invalid message", b"\x00" * 32])
def test_eddsa_verify_fail_wrong_message(msg: bytes, sign_command: TsL3EddsaSignCommand, sign_result: TsL3EddsaSignResult, host: Host):
    command = TsL3EddsaVerifyCommand(
        slot=sign_command.slot.value, 
        msg=msg,
        r=sign_result.r.value,
        s=sign_result.s.value,
    )
    result = host.send_command(command)
    
    assert isinstance(result, TsL3EddsaVerifyResult)
    assert result.result.value == L3ResultFieldEnum.FAIL


