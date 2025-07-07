from typing import Any, Dict

import pytest
from _pytest.fixtures import SubRequest

from tests.test_crypto.test_eddsa.test_eddsa import (
    _VECTORS_TROPIC,  # type: ignore[import]
)
from tvl.api.l3_api import (
    TsL3EddsaSignCommand,
    TsL3EddsaSignResult,
    TsL3EddsaVerifyCommand,
    TsL3EddsaVerifyResult,
)
from tvl.constants import L3ResultFieldEnum
from tvl.crypto.eddsa import eddsa_key_setup
from tvl.host.host import Host
from tvl.messages.randomize import randomize
from tvl.targets.model.configuration_object_impl import ConfigObjectRegisterAddressEnum
from tvl.targets.model.internal.configuration_object import REGISTER_MASK
from tvl.targets.model.internal.ecc_keys import Origins

from ..utils import UtilsEcc


@pytest.fixture()
def slot(model_configuration: Dict[str, Any], request: SubRequest):
    slot = request.param
    vector = _VECTORS_TROPIC[(slot % len(_VECTORS_TROPIC))]  # type: ignore
    s, prefix, a = eddsa_key_setup(vector.k)  # type: ignore
    model_configuration.update(
        {
            "r_ecc_keys": {
                slot: {
                    "s": s,
                    "prefix": prefix,
                    "a": a,
                    "origin": Origins.ECC_KEY_STORE,
                }
            }
        }
    )
    yield slot


@pytest.fixture(params=["slot"])
def unauthorized_slot(model_configuration: Dict[str, Any], slot: int):
    model_configuration.update(
        {
            "i_config": {
                ConfigObjectRegisterAddressEnum.CFG_UAP_EDDSA_VERIFY.name.lower(): ~(
                    0xFF << ((slot // 8) * 8)
                )
                & REGISTER_MASK,
                # ensure that the users have the rights to read all the i-config registers
                ConfigObjectRegisterAddressEnum.CFG_UAP_I_CONFIG_READ.name.lower(): 0x0000_FFFF,
            }
        }
    )
    yield slot


@pytest.fixture(params=["slot"])
def sign_command(slot: int) -> TsL3EddsaSignCommand:
    return randomize(TsL3EddsaSignCommand, slot=slot, msg=b"test message")


@pytest.fixture()
def sign_result(sign_command: TsL3EddsaSignCommand, host: Host) -> TsL3EddsaSignResult:
    # Send the sign command to the host and return the result
    sign_result = host.send_command(sign_command)
    assert isinstance(sign_result, TsL3EddsaSignResult)
    return sign_result


@pytest.mark.parametrize("slot", UtilsEcc.VALID_INDICES, indirect=True)
def test_eddsa_verify_ok_on_valid_slot(
    sign_command: TsL3EddsaSignCommand, sign_result: TsL3EddsaSignResult, host: Host
):
    command = TsL3EddsaVerifyCommand(
        slot=sign_command.slot.value,
        msg=sign_command.msg.value,
        r=sign_result.r.value,
        s=sign_result.s.value,
    )
    result = host.send_command(command)

    assert isinstance(result, TsL3EddsaVerifyResult)
    assert result.result.value == L3ResultFieldEnum.OK


@pytest.mark.parametrize("slot", UtilsEcc.VALID_INDICES, indirect=True)
def test_eddsa_verify_unauthorized_on_forbidden_slot(
    unauthorized_slot: int,
    sign_command: TsL3EddsaSignCommand,
    sign_result: TsL3EddsaSignResult,
    host: Host,
):
    assert unauthorized_slot == sign_command.slot.value
    command = TsL3EddsaVerifyCommand(
        slot=sign_command.slot.value,
        msg=sign_command.msg.value,
        r=sign_result.r.value,
        s=sign_result.s.value,
    )
    result = host.send_command(command)

    assert isinstance(result, TsL3EddsaVerifyResult)
    assert result.result.value == L3ResultFieldEnum.UNAUTHORIZED


@pytest.mark.parametrize("slot", UtilsEcc.INVALID_INDICES[:10], indirect=True)
def test_eddsa_verify_unauthorized_on_invalid_slot(slot: int, host: Host):
    command = TsL3EddsaVerifyCommand(
        slot=slot,
        msg=b"",
        r=b"\x00" * 32,
        s=b"\x00" * 32,
    )
    result = host.send_command(command)

    assert isinstance(result, TsL3EddsaVerifyResult)
    assert result.result.value == L3ResultFieldEnum.UNAUTHORIZED


@pytest.mark.parametrize("slot", UtilsEcc.VALID_INDICES, indirect=True)
@pytest.mark.parametrize("r,s", [(None, b"\x00" * 32), (b"\x01" * 32, None)])
def test_eddsa_verify_fail_on_wrong_signature(
    r: bytes,
    s: bytes,
    sign_command: TsL3EddsaSignCommand,
    sign_result: TsL3EddsaSignResult,
    host: Host,
):
    command = TsL3EddsaVerifyCommand(
        slot=sign_command.slot.value,
        msg=sign_command.msg.value,
        r=r or sign_result.r.value,
        s=s or sign_result.s.value,
    )
    result = host.send_command(command)

    assert isinstance(result, TsL3EddsaVerifyResult)
    assert result.result.value == L3ResultFieldEnum.FAIL


@pytest.mark.parametrize("slot", UtilsEcc.VALID_INDICES, indirect=True)
@pytest.mark.parametrize("msg", [b"", b"invalid message", b"\x00" * 32])
def test_eddsa_verify_fail_on_wrong_message(
    msg: bytes,
    sign_command: TsL3EddsaSignCommand,
    sign_result: TsL3EddsaSignResult,
    host: Host,
):
    command = TsL3EddsaVerifyCommand(
        slot=sign_command.slot.value,
        msg=msg,
        r=sign_result.r.value,
        s=sign_result.s.value,
    )
    result = host.send_command(command)

    assert isinstance(result, TsL3EddsaVerifyResult)
    assert result.result.value == L3ResultFieldEnum.FAIL


@pytest.mark.parametrize(
    "slot", UtilsEcc.VALID_INDICES
)  # !is not indirect, side effect of the fixture - key stored in slot - is not called
def test_eddsa_verify_invalid_key_on_empty_slot(slot: int, host: Host):
    command = TsL3EddsaVerifyCommand(
        slot=slot,
        msg=b"",
        r=b"\x00" * 32,
        s=b"\x00" * 32,
    )
    result = host.send_command(command)

    assert isinstance(result, TsL3EddsaVerifyResult)
    assert result.result.value == TsL3EddsaVerifyResult.ResultEnum.INVALID_KEY
