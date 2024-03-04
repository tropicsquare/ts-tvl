# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
import random
from typing import Any, Dict

import pytest

from tvl.api.l2_api import (
    TsL2GetInfoReqRequest,
    TsL2GetInfoReqResponse,
    TsL2ResendReqRequest,
)
from tvl.constants import L2IdFieldEnum, L2StatusEnum
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model

_CHIP_ID = os.urandom(128)
_RESEND_MAX_COUNT = random.randint(1, 5)  # send at least one resend request


@pytest.fixture()
def model_configuration(model_configuration: Dict[str, Any]):
    model_configuration.update(
        {
            "chip_id": _CHIP_ID,
            "resend_max_count": _RESEND_MAX_COUNT,
            "busy_iter": [False],
        }
    )
    yield model_configuration


@pytest.fixture()
def get_info_response(host: Host):
    # Send first request
    get_info_request = TsL2GetInfoReqRequest(
        object_id=TsL2GetInfoReqRequest.ObjectIdEnum.CHIP_ID, block_index=0
    )
    get_info_response_ = host.send_request(get_info_request)
    assert isinstance(get_info_response_, TsL2GetInfoReqResponse)
    assert get_info_response_.object.to_bytes() == _CHIP_ID
    yield get_info_response_


def test_response_in_buffer(
    host: Host, model: Tropic01Model, get_info_response: TsL2GetInfoReqResponse
):
    # Send resend request
    for _ in range(_RESEND_MAX_COUNT):
        resend_response = host.send_request(TsL2ResendReqRequest())
        assert resend_response == get_info_response

    # The chip sends status = NO_RESP
    # as soon as the resend counter has reached its maximum
    model.spi_drive_csn_low()
    model.spi_send(TsL2ResendReqRequest().to_bytes())
    model.spi_drive_csn_high()

    model.spi_drive_csn_low()
    _, status = model.spi_send(bytes([L2IdFieldEnum.GET_RESP]) + bytes(1))
    model.spi_drive_csn_high()

    assert status == L2StatusEnum.NO_RESP


@pytest.mark.skip(reason="TODO")
def test_no_response_in_buffer():
    pass
