# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from tvl.api.l2_api import TsL2GetLogRequest, TsL2GetLogResponse
from tvl.constants import L2StatusEnum
from tvl.host.host import Host


def test_mutable_fw_erase_req(host: Host):
    response = host.send_request(TsL2GetLogRequest())
    assert isinstance(response, TsL2GetLogResponse)
    assert response.status.value == L2StatusEnum.REQ_OK
    assert response.data_field_bytes == b""
