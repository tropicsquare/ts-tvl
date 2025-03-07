from typing import Any, Dict

import pytest

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
    assert model.spi_fsm.response_buffer.latest() != b""
    yield host


def test_sleep_mode(host: Host, model: Tropic01Model):
    response = host.send_request(
        TsL2SleepRequest(sleep_kind=TsL2SleepRequest.SleepKindEnum.SLEEP_MODE)
    )

    assert response.status.value == L2StatusEnum.REQ_OK
    assert isinstance(response, TsL2SleepResponse)
    assert not model.session.is_session_valid()
    assert model.command_buffer.is_empty()
    assert model.spi_fsm.response_buffer.latest() == response.to_bytes()


@pytest.mark.parametrize(
    "sleep_kind", sample_outside(TsL2SleepRequest.SleepKindEnum, nb_bytes=1, k=10)
)
def test_invalid_sleep_kind(host: Host, sleep_kind: int):
    response = host.send_request(TsL2SleepRequest(sleep_kind=sleep_kind))

    assert response.status.value == L2StatusEnum.GEN_ERR


@pytest.fixture
def sleep_kind(model_configuration: Dict[str, Any]):
    model_configuration["i_config"] = {"cfg_sleep_mode": 0}
    yield TsL2SleepRequest.SleepKindEnum.SLEEP_MODE


def test_disabled(sleep_kind: int, host: Host):
    response = host.send_request(TsL2SleepRequest(sleep_kind=sleep_kind))

    assert response.status.value == L2StatusEnum.RESP_DISABLED
