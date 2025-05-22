from itertools import chain
from typing import Any, Callable, Dict

import pytest
from _pytest.fixtures import SubRequest

from tvl.api.l3_api import TsL3EccKeyStoreCommand, TsL3EccKeyStoreResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.messages.randomize import randomize
from tvl.targets.model.tropic01_model import Tropic01Model

from ..utils import UtilsEcc, as_slow, one_outside


def _isnone(x: Any) -> bool:
    return x is None


def _isnotnone(x: Any) -> bool:
    return not _isnone(x)


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10))
@pytest.mark.parametrize(
    "key, status, check",
    chain(
        (
            pytest.param(
                UtilsEcc.get_valid_ecdsa_private_key(),
                L3ResultFieldEnum.OK,
                _isnotnone,
                id="valid_private_key",
            )
            for _ in range(5)
        ),
        (
            pytest.param(
                UtilsEcc.get_invalid_ecdsa_private_key(),
                L3ResultFieldEnum.FAIL,
                _isnone,
                id="invalid_private_key",
            )
            for _ in range(5)
        ),
        [
            pytest.param(
                0, L3ResultFieldEnum.FAIL, _isnone, id="invalid_private_key_zero"
            )
        ],
    ),
)
def test_storing_ecdsa(
    host: Host,
    model: Tropic01Model,
    slot: int,
    key: bytes,
    status: L3ResultFieldEnum,
    check: Callable[[Any], bool],
):
    assert model.r_ecc_keys.slots[slot] is None
    command = TsL3EccKeyStoreCommand(
        slot=slot, k=key, curve=TsL3EccKeyStoreCommand.CurveEnum.P256
    )
    result = host.send_command(command)

    assert result.result.value == status
    assert isinstance(result, TsL3EccKeyStoreResult)
    assert check(model.r_ecc_keys.slots[slot])


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10))
def test_storing_eddsa(host: Host, model: Tropic01Model, slot: int):
    assert model.r_ecc_keys.slots[slot] is None
    command = randomize(
        TsL3EccKeyStoreCommand,
        slot=slot,
        curve=TsL3EccKeyStoreCommand.CurveEnum.ED25519,
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
    command = randomize(TsL3EccKeyStoreCommand, slot=slot)
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
    assert isinstance(result, TsL3EccKeyStoreResult)
    assert model.r_ecc_keys.slots[slot] == before


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.VALID_INDICES, 10))
def test_invalid_curve(host: Host, model: Tropic01Model, slot: int):
    assert model.r_ecc_keys.slots[slot] is None
    command = randomize(
        TsL3EccKeyStoreCommand,
        slot=slot,
        curve=one_outside(TsL3EccKeyStoreCommand.CurveEnum),
    )
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.FAIL
    assert isinstance(result, TsL3EccKeyStoreResult)
    assert model.r_ecc_keys.slots[slot] is None


@pytest.mark.parametrize("slot", as_slow(UtilsEcc.INVALID_INDICES, 10))
def test_invalid_slot(host: Host, model: Tropic01Model, slot: int):
    assert model.r_ecc_keys.slots[slot] is None
    command = randomize(TsL3EccKeyStoreCommand, slot=slot)
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.UNAUTHORIZED
    assert model.r_ecc_keys.slots[slot] is None
