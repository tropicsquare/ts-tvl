from typing import List

import pytest

from tvl.api.l2_api import TsL2HandshakeRequest, TsL2StartupRequest, TsL2StartupResponse
from tvl.constants import L2StatusEnum
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model


def _known_startup_ids() -> List[int]:
    return list(TsL2StartupRequest.StartupIdEnum)


def _unknown_startup_ids() -> List[int]:
    return [i for i in range(256) if i not in set(_known_startup_ids())]


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
    yield host


@pytest.mark.parametrize("startup_id", _known_startup_ids())
def test_startup_req(host: Host, model: Tropic01Model, startup_id: int):
    response = host.send_request(TsL2StartupRequest(startup_id=startup_id))
    assert isinstance(response, TsL2StartupResponse)
    assert response.status.value == L2StatusEnum.REQ_OK
    assert not model.session.is_session_valid()
    assert not host.session.is_session_valid()


@pytest.mark.parametrize("startup_id", _unknown_startup_ids())
def test_startup_req_unknown_startup_id(
    host: Host, model: Tropic01Model, startup_id: int
):
    response = host.send_request(TsL2StartupRequest(startup_id=startup_id))
    assert isinstance(response, TsL2StartupResponse)
    assert response.status.value == L2StatusEnum.GEN_ERR
    assert model.session.is_session_valid()
    assert host.session.is_session_valid()
