# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
from collections import ChainMap
from typing import Any, Dict, Mapping

import pytest
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from tvl.api.l2_api import TsL2HandshakeReqRequest
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model


class BaseTest:
    CONFIGURATION: Dict[str, Any] = {}

    @pytest.fixture(scope="class")
    def _default_configuration(self):
        tropic_priv_key_ = X25519PrivateKey.generate()
        tropic_priv_key_bytes = tropic_priv_key_.private_bytes_raw()
        tropic_pub_key_bytes = tropic_priv_key_.public_key().public_bytes_raw()

        host_priv_key_ = X25519PrivateKey.generate()
        host_priv_key_bytes = host_priv_key_.private_bytes_raw()
        host_pub_key_bytes = host_priv_key_.public_key().public_bytes_raw()

        yield {
            "host": {
                "s_h_priv": host_priv_key_bytes,
                "s_h_pub": host_pub_key_bytes,
                "s_t_pub": tropic_pub_key_bytes,
                "pairing_key_index": (pki := random.randint(1, 4)),
            },
            "model": {
                "s_t_priv": tropic_priv_key_bytes,
                "s_t_pub": tropic_pub_key_bytes,
                "i_pairing_keys": {
                    pki: {
                        "value": host_pub_key_bytes,
                    },
                },
            },
        }

    @pytest.fixture(scope="class")
    def default_configuration(self, _default_configuration: Dict[str, Any]):
        """Override if needed"""
        yield _default_configuration

    @pytest.fixture(scope="class")
    def _model_configuration(self, default_configuration: Dict[str, Any]):
        yield ChainMap(
            self.CONFIGURATION.get("model", {}), default_configuration["model"]
        )

    @pytest.fixture(scope="class")
    def _host_configuration(self, default_configuration: Dict[str, Any]):
        yield ChainMap(
            self.CONFIGURATION.get("host", {}), default_configuration["host"]
        )

    @pytest.fixture(scope="class")
    def _model(self, _model_configuration: Mapping[str, Any]):
        yield Tropic01Model.from_dict(_model_configuration)

    @pytest.fixture(scope="class")
    def model(self, _model: Tropic01Model):
        """Override if needed"""
        yield _model

    @pytest.fixture(scope="class")
    def _host(self, model: Tropic01Model, _host_configuration: Mapping[str, Any]):
        with Host.from_dict(_host_configuration).set_target(model) as host_:
            yield host_

    @pytest.fixture(scope="class")
    def host(self, _host: Host):
        """Override if needed"""
        yield _host


class BaseTestSecureChannel(BaseTest):
    @pytest.fixture(scope="class")
    def host(self, _host: Host):
        # Execute handshake before sending L3-level commands
        _host.send_request(
            TsL2HandshakeReqRequest(
                e_hpub=_host.session.create_handshake_request(),
                pkey_index=_host.pairing_key_index,
            )
        )
        yield _host
