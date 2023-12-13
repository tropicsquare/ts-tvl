# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
import random

import pytest

from tvl.targets.model.internal.ecc_keys import (
    KEY_SIZE,
    CurveMismatchError,
    EccKey,
    ECCKeyDoesNotExistInSlotError,
    ECCKeyExistsInSlotError,
    EccKeys,
    ECCKeySubClassNotFoundError,
    ECDSAKeyMemLayout,
    EdDSAKeyMemLayout,
    Origins,
)


def _gen_key() -> bytes:
    return os.urandom(KEY_SIZE)


def _get_int() -> int:
    return random.randint(0, 10)


def test_ecc_key_find_subclass():
    assert EccKey.find_subclass_from_curve((c := ECDSAKeyMemLayout).CURVE) is c
    assert EccKey.find_subclass_from_curve((c := EdDSAKeyMemLayout).CURVE) is c
    with pytest.raises(ECCKeySubClassNotFoundError):
        EccKey.find_subclass_from_curve(0)


def test_ecc_key_dict():
    init_dict = {
        "a": os.urandom(32),
        "d": os.urandom(32),
        "w": os.urandom(64),
        "origin": Origins.Ecc_Key_Generate,
    }

    ecc_key_0 = ECDSAKeyMemLayout(**init_dict)  # type: ignore
    assert ecc_key_0.to_dict() == init_dict

    ecc_key_1 = ECDSAKeyMemLayout.from_dict(init_dict)
    assert ecc_key_1.to_dict() == init_dict

    ecc_key_2 = EccKey.from_dict(init_dict)
    assert ecc_key_2.to_dict() == init_dict

    with pytest.raises(ECCKeySubClassNotFoundError):
        EccKey.from_dict({"incorrect": b"incorrect"})


def test_store():
    ecc = EccKeys()

    slot_0 = _get_int()
    assert ecc.slots[slot_0] is None
    ecc.store(
        slot_0,
        (curve_type_0 := ECDSAKeyMemLayout).CURVE,
        _gen_key(),
        Origins.Ecc_Key_Generate,
    )
    assert isinstance(ecc.slots[slot_0], curve_type_0)

    with pytest.raises(ECCKeyExistsInSlotError):
        ecc.store(
            slot_0,
            ECDSAKeyMemLayout.CURVE,
            _gen_key(),
            Origins.Ecc_Key_Generate,
        )
    assert isinstance(ecc.slots[slot_0], curve_type_0)

    slot_1 = slot_0 + 1
    assert ecc.slots[slot_1] is None
    ecc.store(
        slot_1,
        (curve_type_1 := EdDSAKeyMemLayout).CURVE,
        _gen_key(),
        Origins.Ecc_Key_Generate,
    )
    assert isinstance(ecc.slots[slot_0], curve_type_0)
    assert isinstance(ecc.slots[slot_1], curve_type_1)


def test_read():
    ecc = EccKeys()

    slot_0 = _get_int()
    ecc.store(
        slot_0,
        (curve_type_0 := ECDSAKeyMemLayout).CURVE,
        _gen_key(),
        Origins.Ecc_Key_Generate,
    )

    curve, a, origin = ecc.read(slot_0)
    assert origin == Origins.Ecc_Key_Generate
    assert curve == curve_type_0.CURVE
    assert isinstance(a, bytes)

    with pytest.raises(ECCKeyDoesNotExistInSlotError):
        ecc.read(slot_0 + 1)


def test_erase():
    ecc = EccKeys()

    slot_0 = _get_int()
    assert ecc.slots[slot_0] is None
    ecc.store(
        slot_0,
        (curve_type_0 := ECDSAKeyMemLayout).CURVE,
        _gen_key(),
        Origins.Ecc_Key_Generate,
    )
    assert isinstance(ecc.slots[slot_0], curve_type_0)

    ecc.erase(slot_0)
    assert ecc.slots[slot_0] is None

    slot_1 = slot_0 + 1
    assert ecc.slots[slot_1] is None
    with pytest.raises(ECCKeyDoesNotExistInSlotError):
        ecc.erase(slot_1)
    assert ecc.slots[slot_1] is None


def test_signing():
    ecc = EccKeys()

    ecc.store(
        slot_0 := _get_int(),
        ECDSAKeyMemLayout.CURVE,
        _gen_key(),
        Origins.Ecc_Key_Generate,
    )
    ecc.store(
        slot_1 := slot_0 + 1,
        EdDSAKeyMemLayout.CURVE,
        _gen_key(),
        Origins.Ecc_Key_Generate,
    )

    ecc.ecdsa_sign(slot_0, b"message_hash", b"handshake_hash", b"nonce")
    with pytest.raises(CurveMismatchError):
        ecc.ecdsa_sign(slot_1, b"message_hash", b"handshake_hash", b"nonce")

    ecc.eddsa_sign(slot_1, b"message", b"handshake_hash", b"nonce")
    with pytest.raises(CurveMismatchError):
        ecc.eddsa_sign(slot_0, b"message", b"handshake_hash", b"nonce")


def test_dict():
    key_init_dict = {
        "a": os.urandom(32),
        "d": os.urandom(32),
        "w": os.urandom(64),
        "origin": Origins.Ecc_Key_Generate,
    }
    ecc_init_dict = {(slot := _get_int()): key_init_dict}
    ecc = EccKeys.from_dict(ecc_init_dict)

    assert ecc.slots[slot].to_dict() == key_init_dict  # type: ignore
    assert ecc.to_dict() == ecc_init_dict
