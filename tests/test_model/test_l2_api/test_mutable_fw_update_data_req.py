# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
import random

from tvl.api.l2_api import (
    TsL2MutableFwUpdateDataRequest,
    TsL2MutableFwUpdateDataResponse,
)
from tvl.constants import L2StatusEnum
from tvl.host.host import Host


def test_mutable_fw_update_req(host: Host):
    response = host.send_request(
        TsL2MutableFwUpdateDataRequest(
            hash=os.urandom(32),
            offset=os.urandom(2),
            data=os.urandom(random.randint(4, 220)),
        )
    )
    assert isinstance(response, TsL2MutableFwUpdateDataResponse)
    assert response.status.value == L2StatusEnum.REQ_OK
