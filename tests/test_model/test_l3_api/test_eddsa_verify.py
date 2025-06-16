from typing import Any, Dict
import hashlib

import pytest
from _pytest.fixtures import SubRequest

from tvl.api.l3_api import TsL3EddsaSignCommand, TsL3EddsaSignResult, TsL3EddsaVerifyCommand, TsL3EddsaVerifyResult
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
def test_eddsa_verify_valid_signature(slot: int, host: Host):
    """Test that EDDSA_Verify correctly validates a signature created by EDDSA_Sign."""
    # First, sign a message using EDDSA_Sign
    message = b"Hello, World! This is a test message for EdDSA verification."
    msg_hash = hashlib.sha256(message).digest()
    
    sign_command = TsL3EddsaSignCommand(slot=slot, msg=message)
    sign_result = host.send_command(sign_command)
    
    assert sign_result.result.value == L3ResultFieldEnum.OK
    assert isinstance(sign_result, TsL3EddsaSignResult)
    
    # Now verify the signature using EDDSA_Verify
    verify_command = TsL3EddsaVerifyCommand(
        slot=slot,
        msg_hash=msg_hash,
        r=sign_result.r.value,
        s=sign_result.s.value
    )
    verify_result = host.send_command(verify_command)
    
    assert verify_result.result.value == TsL3EddsaVerifyResult.ResultEnum.OK
    assert isinstance(verify_result, TsL3EddsaVerifyResult)


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10), indirect=True)
def test_eddsa_verify_invalid_signature(slot: int, host: Host):
    """Test that EDDSA_Verify correctly rejects an invalid signature."""
    message = b"Hello, World! This is a test message for EdDSA verification."
    msg_hash = hashlib.sha256(message).digest()
    
    # Create an invalid signature (all zeros)
    invalid_r = b'\x00' * 32
    invalid_s = b'\x00' * 32
    
    verify_command = TsL3EddsaVerifyCommand(
        slot=slot,
        msg_hash=msg_hash,
        r=invalid_r,
        s=invalid_s
    )
    verify_result = host.send_command(verify_command)
    
    assert verify_result.result.value == TsL3EddsaVerifyResult.ResultEnum.FAIL
    assert isinstance(verify_result, TsL3EddsaVerifyResult)


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10), indirect=True)
def test_eddsa_verify_wrong_message_hash(slot: int, host: Host):
    """Test that EDDSA_Verify correctly rejects a signature for a different message."""
    # First, sign a message using EDDSA_Sign
    original_message = b"Original message"
    different_message = b"Different message"
    different_msg_hash = hashlib.sha256(different_message).digest()
    
    sign_command = TsL3EddsaSignCommand(slot=slot, msg=original_message)
    sign_result = host.send_command(sign_command)
    
    assert sign_result.result.value == L3ResultFieldEnum.OK
    assert isinstance(sign_result, TsL3EddsaSignResult)
    
    # Try to verify the signature with a different message hash
    verify_command = TsL3EddsaVerifyCommand(
        slot=slot,
        msg_hash=different_msg_hash,
        r=sign_result.r.value,
        s=sign_result.s.value
    )
    verify_result = host.send_command(verify_command)
    
    assert verify_result.result.value == TsL3EddsaVerifyResult.ResultEnum.FAIL
    assert isinstance(verify_result, TsL3EddsaVerifyResult)


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10))
def test_eddsa_verify_no_key(host: Host, slot: int):
    """Test that EDDSA_Verify returns INVALID_KEY when no key exists in the slot."""
    msg_hash = hashlib.sha256(b"test message").digest()
    
    verify_command = TsL3EddsaVerifyCommand(
        slot=slot,
        msg_hash=msg_hash,
        r=b'\x00' * 32,
        s=b'\x00' * 32
    )
    verify_result = host.send_command(verify_command)
    
    assert verify_result.result.value == TsL3EddsaVerifyResult.ResultEnum.INVALID_KEY
    assert not isinstance(verify_result, TsL3EddsaVerifyResult)


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.INVALID_INDICES, 10))
def test_eddsa_verify_invalid_slot(host: Host, slot: int):
    """Test that EDDSA_Verify returns UNAUTHORIZED for invalid slot indices."""
    msg_hash = hashlib.sha256(b"test message").digest()
    
    verify_command = TsL3EddsaVerifyCommand(
        slot=slot,
        msg_hash=msg_hash,
        r=b'\x00' * 32,
        s=b'\x00' * 32
    )
    verify_result = host.send_command(verify_command)
    
    assert verify_result.result.value == L3ResultFieldEnum.UNAUTHORIZED 