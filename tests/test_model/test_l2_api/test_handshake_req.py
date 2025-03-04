import random
from contextlib import nullcontext
from typing import Any, Callable, ContextManager, Dict

import pytest
from _pytest.fixtures import SubRequest

from tvl.api.l2_api import TsL2HandshakeRequest, TsL2HandshakeResponse
from tvl.constants import L2StatusEnum
from tvl.host.host import Host
from tvl.messages.l2_messages import L2Response
from tvl.targets.model.internal.pairing_keys import SlotState


def sucessful_handshake(response: L2Response) -> bool:
    return (
        isinstance(response, TsL2HandshakeResponse)
        and response.status.value == L2StatusEnum.REQ_OK
    )


def handshake_error(response: L2Response) -> bool:
    return (
        not isinstance(response, TsL2HandshakeResponse)
        and response.status.value == L2StatusEnum.HSK_ERR
    )


def error(_: L2Response):
    """should not be called"""
    return False


@pytest.fixture()
def configuration(configuration: Dict[str, Dict[str, Any]], request: SubRequest):
    params: Dict[str, Any] = request.param
    configuration["model"].update(params.get("model", {}))
    configuration["host"].update(params.get("host", {}))
    yield configuration


@pytest.mark.parametrize(
    "configuration, context, outcome",
    [
        pytest.param(
            {},
            nullcontext(),
            sucessful_handshake,
            id="successful_handshake",
        ),
        pytest.param(
            {
                "host": {"pairing_key_index": (pki := random.randint(0, 4))},
                "model": {"i_pairing_keys": {pki: {"state": SlotState.BLANK}}},
            },
            nullcontext(),
            handshake_error,
            id="error_blank_key",
        ),
        pytest.param(
            {
                "host": {"pairing_key_index": (pki := random.randint(0, 4))},
                "model": {"i_pairing_keys": {pki: {"state": SlotState.INVALID}}},
            },
            nullcontext(),
            handshake_error,
            id="error_invalid_key",
        ),
        pytest.param(
            {"model": {"s_t_priv": None}},
            pytest.raises(RuntimeError),
            error,
            id="error_model_not_paired",
        ),
        pytest.param(
            {},
            nullcontext(),
            error,
            marks=[pytest.mark.skip(reason="Implement this test case")],
            id="error_wrong_key",
        ),
    ],
    indirect=["configuration"],
)
def test_handshake(
    host: Host, context: ContextManager[Any], outcome: Callable[[L2Response], bool]
):
    request = TsL2HandshakeRequest(
        e_hpub=host.session.create_handshake_request(),
        pkey_index=host.pairing_key_index,
    )

    with context:
        response = host.send_request(request)
        assert outcome(response)
