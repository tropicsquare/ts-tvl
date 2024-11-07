# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict

import pytest
from _pytest.fixtures import SubRequest

from tvl.api.l2_api import TsL2HandshakeRequest, TsL2SleepRequest, TsL2SleepResponse
from tvl.constants import L2StatusEnum
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model

from ..utils import sample_outside


@pytest.fixture()
def host(host: Host, model: Tropic01Model):
    # Execute handshake before sending L3-level commands
    host.send_request(
        TsL2HandshakeRequest(
            e_hpub=host.session.create_handshake_request(),
            pkey_index=host.pairing_key_index,
        )
    )
    assert model.session.is_session_valid()
    assert host.session.is_session_valid()
    assert model.response_buffer.latest() != b""
    yield host


def test_sleep_mode(host: Host, model: Tropic01Model):
    response = host.send_request(
        TsL2SleepRequest(sleep_kind=TsL2SleepRequest.SleepKindEnum.SLEEP_MODE)
    )

    assert response.status.value == L2StatusEnum.REQ_OK
    assert isinstance(response, TsL2SleepResponse)
    assert not model.session.is_session_valid()
    assert model.command_buffer.is_empty()
    assert model.response_buffer.latest() == response.to_bytes()


@pytest.mark.xfail(reason="Response buffer to be emptied upon deep sleep mode request")
def test_deep_sleep_mode(host: Host, model: Tropic01Model):
    response = host.send_request(
        TsL2SleepRequest(sleep_kind=TsL2SleepRequest.SleepKindEnum.DEEP_SLEEP_MODE)
    )

    assert response.status.value == L2StatusEnum.REQ_OK
    assert isinstance(response, TsL2SleepResponse)
    assert not model.session.is_session_valid()
    assert model.command_buffer.is_empty()
    assert model.response_buffer.is_empty()
    assert model.response_buffer.latest() == b""


@pytest.mark.parametrize(
    "sleep_kind", sample_outside(TsL2SleepRequest.SleepKindEnum, nb_bytes=1, k=10)
)
def test_invalid_sleep_kind(host: Host, sleep_kind: int):
    response = host.send_request(TsL2SleepRequest(sleep_kind=sleep_kind))

    assert response.status.value == L2StatusEnum.GEN_ERR


@pytest.fixture(
    params=[
        pytest.param(
            (_m := TsL2SleepRequest.SleepKindEnum.SLEEP_MODE, 0b10), id=str(_m)
        ),
        pytest.param(
            (_m := TsL2SleepRequest.SleepKindEnum.DEEP_SLEEP_MODE, 0b01), id=str(_m)
        ),
    ]
)
def sleep_kind(model_configuration: Dict[str, Any], request: SubRequest):
    _sleep_kind, register_value = request.param
    model_configuration["i_config"] = {"cfg_sleep_mode": register_value}
    yield _sleep_kind


def test_disabled(sleep_kind: int, host: Host):
    response = host.send_request(TsL2SleepRequest(sleep_kind=sleep_kind))

    assert response.status.value == L2StatusEnum.RESP_DISABLED
