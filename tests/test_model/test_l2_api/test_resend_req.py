import os
import random
from typing import Any, Dict

import pytest

from tvl.api.l2_api import TsL2GetInfoRequest, TsL2GetInfoResponse, TsL2ResendRequest
from tvl.constants import L2StatusEnum
from tvl.host.host import Host
from tvl.messages.randomize import randomize

_CHIP_ID = os.urandom(128)


@pytest.fixture()
def model_configuration(model_configuration: Dict[str, Any]):
    model_configuration.update(
        {
            "chip_id": _CHIP_ID,
            "busy_iter": [False],
        }
    )
    yield model_configuration


def test_response_in_buffer(host: Host):
    # Send request beforehand
    get_info_request = randomize(
        TsL2GetInfoRequest, object_id=TsL2GetInfoRequest.ObjectIdEnum.CHIP_ID
    )
    get_info_response = host.send_request(get_info_request)

    assert isinstance(get_info_response, TsL2GetInfoResponse)
    assert get_info_response.status.value == L2StatusEnum.REQ_OK
    assert get_info_response.object.to_bytes() == _CHIP_ID

    for _ in range(random.randint(1, 5)):
        resend_response = host.send_request(TsL2ResendRequest())
        assert resend_response == get_info_response


def test_no_response_in_buffer(host: Host):
    for _ in range(random.randint(1, 5)):
        resend_response = host.send_request(TsL2ResendRequest())
        assert resend_response.status.value == L2StatusEnum.GEN_ERR
