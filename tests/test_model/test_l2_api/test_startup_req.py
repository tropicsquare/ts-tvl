# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from typing import Any, List, Mapping

import pytest

from tvl.api.l2_api import (
    TsL2HandshakeReqRequest,
    TsL2StartupReqRequest,
    TsL2StartupReqResponse,
)
from tvl.constants import L2StatusEnum
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model

from ..base_test import BaseTest


def _known_startup_ids() -> List[int]:
    return list(TsL2StartupReqRequest.StartupIdEnum)


def _unknown_startup_ids() -> List[int]:
    return [i for i in range(256) if i not in set(TsL2StartupReqRequest.StartupIdEnum)]


class TestStartupReq(BaseTest):
    @pytest.fixture(scope="function")
    def model(self, _model_configuration: Mapping[str, Any]):
        yield Tropic01Model.from_dict(_model_configuration)

    @pytest.fixture(scope="function")
    def host(self, model: Tropic01Model, _host_configuration: Mapping[str, Any]):
        _host = Host.from_dict(_host_configuration).set_target(model)
        # Execute handshake before sending L3-level commands
        _host.send_request(
            TsL2HandshakeReqRequest(
                e_hpub=_host.session.create_handshake_request(),
                pkey_index=_host.pairing_key_index,
            )
        )
        assert model.session.is_session_valid()
        assert _host.session.is_session_valid()
        yield _host

    @pytest.mark.parametrize("startup_id", _known_startup_ids())
    def test_startup_req(self, host: Host, model: Tropic01Model, startup_id: int):
        response = host.send_request(TsL2StartupReqRequest(startup_id=startup_id))
        assert isinstance(response, TsL2StartupReqResponse)
        assert response.status.value == L2StatusEnum.REQ_OK
        assert not model.session.is_session_valid()
        assert not host.session.is_session_valid()

    @pytest.mark.parametrize("startup_id", _unknown_startup_ids())
    def test_startup_req_unknown_startup_id(
        self, host: Host, model: Tropic01Model, startup_id: int
    ):
        response = host.send_request(TsL2StartupReqRequest(startup_id=startup_id))
        assert isinstance(response, TsL2StartupReqResponse)
        assert response.status.value == L2StatusEnum.GEN_ERR
        assert model.session.is_session_valid()
        assert host.session.is_session_valid()
