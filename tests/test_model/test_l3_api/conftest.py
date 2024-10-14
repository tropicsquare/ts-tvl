# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import pytest

from tvl.api.l2_api import TsL2HandshakeRequest
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model


@pytest.fixture(scope="function")
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
