# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0


from tvl.api.l2_api import (
    TsL2MutableFwUpdateDataRequest,
    TsL2MutableFwUpdateDataResponse,
)
from tvl.constants import L2StatusEnum
from tvl.host.host import Host
from tvl.messages.randomize import randomize


def test_mutable_fw_update_req(host: Host):
    response = host.send_request(randomize(TsL2MutableFwUpdateDataRequest))
    assert isinstance(response, TsL2MutableFwUpdateDataResponse)
    assert response.status.value == L2StatusEnum.REQ_OK
