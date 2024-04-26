# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import random
from typing import Any, Dict

import pytest
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from tvl.constants import S_HI_PUB_NB_SLOTS
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model


@pytest.fixture(scope="function")
def configuration():
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
            "pairing_key_index": (pki := random.randrange(S_HI_PUB_NB_SLOTS)),
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


@pytest.fixture(scope="function")
def model_configuration(configuration: Dict[str, Any]):
    yield configuration["model"]


@pytest.fixture(scope="function")
def host_configuration(configuration: Dict[str, Any]):
    yield configuration["host"]


@pytest.fixture(scope="function")
def model(model_configuration: Dict[str, Any]):
    yield Tropic01Model.from_dict(model_configuration)


@pytest.fixture(scope="function")
def host(model: Tropic01Model, host_configuration: Dict[str, Any]):
    with Host.from_dict(host_configuration).set_target(model) as _host:
        yield _host
