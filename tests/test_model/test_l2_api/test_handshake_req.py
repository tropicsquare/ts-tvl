# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
from contextlib import nullcontext
from typing import Any, ContextManager

import pytest

from tvl.api.l2_api import TsL2HandshakeReqRequest, TsL2HandshakeReqResponse
from tvl.constants import L2StatusEnum
from tvl.host.host import Host
from tvl.messages.l2_messages import L2Response
from tvl.targets.model.internal.pairing_keys import BLANK_VALUE, INVALID_VALUE

from ..base_test import BaseTest


class BaseTestHandshakeReq(BaseTest):
    def test(self, host: Host):
        request = TsL2HandshakeReqRequest(
            e_hpub=host.session.create_handshake_request(),
            pkey_index=host.pairing_key_index,
        )
        with self._context():
            response = host.send_request(request)
            self._check(response)

    def _context(self) -> ContextManager[Any]:
        return nullcontext()

    def _check(self, response: L2Response) -> None:
        pytest.fail(reason="Test not implemented")


class TestSuccessfulHandshakeReq(BaseTestHandshakeReq):
    def _check(self, response: L2Response):
        assert isinstance(response, TsL2HandshakeReqResponse)
        assert response.status.value == L2StatusEnum.REQ_OK


class TestHandshakeReqBlankKey(BaseTestHandshakeReq):
    CONFIGURATION = {
        "host": {"pairing_key_index": (pki := random.randint(0, 4))},
        "model": {"i_pairing_keys": {pki: {"value": BLANK_VALUE}}},
    }

    def _check(self, response: L2Response):
        assert not isinstance(response, TsL2HandshakeReqResponse)
        assert response.status.value == L2StatusEnum.HSK_ERR


class TestHandshakeReqInvalidKey(BaseTestHandshakeReq):
    CONFIGURATION = {
        "host": {"pairing_key_index": (pki := random.randint(0, 4))},
        "model": {"i_pairing_keys": {pki: {"value": INVALID_VALUE}}},
    }

    def _check(self, response: L2Response):
        assert not isinstance(response, TsL2HandshakeReqResponse)
        assert response.status.value == L2StatusEnum.HSK_ERR


class TestHandshakeReqModelNotPaired(BaseTestHandshakeReq):
    CONFIGURATION = {
        "model": {
            "s_t_priv": None,
        }
    }

    def _context(self) -> ContextManager[Any]:
        return pytest.raises(RuntimeError)

    def _check(self, response: L2Response) -> None:
        pass


@pytest.mark.skip(reason="Implement this test case")
class TestHandshakeReqWrongKey(BaseTestHandshakeReq):
    pass
