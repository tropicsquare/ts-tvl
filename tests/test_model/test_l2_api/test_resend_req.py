import os
import random

import pytest

from tvl.api.l2_api import (
    TsL2GetInfoReqRequest,
    TsL2GetInfoReqResponse,
    TsL2ResendReqRequest,
)
from tvl.constants import L2IdFieldEnum, L2StatusEnum
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model

from ..base_test import BaseTest

_CHIP_ID = os.urandom(128)
_RESEND_MAX_COUNT = random.randint(1, 5)  # send at least one resend request


class TestResendReq(BaseTest):
    CONFIGURATION = {
        "model": {
            "chip_id": _CHIP_ID,
            "resend_max_count": _RESEND_MAX_COUNT,
            "busy_iter": [False],
        }
    }

    @pytest.fixture(scope="class")
    def get_info_response(self, host: Host):
        # Send first request
        get_info_request = TsL2GetInfoReqRequest(
            object_id=TsL2GetInfoReqRequest.ObjectIdEnum.CHIP_ID, block_index=0
        )
        get_info_response_ = host.send_request(get_info_request)
        assert isinstance(get_info_response_, TsL2GetInfoReqResponse)
        assert get_info_response_.object.to_bytes() == _CHIP_ID
        yield get_info_response_

    def test_response_in_buffer(
        self,
        host: Host,
        model: Tropic01Model,
        get_info_response: TsL2GetInfoReqResponse,
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
        resp = model.spi_send(bytes([L2IdFieldEnum.GET_RESP]) + bytes(4))
        model.spi_drive_csn_high()

        status = resp[1]
        assert status == L2StatusEnum.NO_RESP


# TODO test no response in fifo
