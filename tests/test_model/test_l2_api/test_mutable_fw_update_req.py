import os
import random

from tvl.api.l2_api import TsL2MutableFwUpdateReqRequest
from tvl.constants import L2StatusEnum
from tvl.host.host import Host

from ..base_test import BaseTest


class TestMutableFwEraseReq(BaseTest):
    def test_mutable_fw_update_req(self, host: Host):
        response = host.send_request(
            TsL2MutableFwUpdateReqRequest(
                bank_id=os.urandom(1),
                offset=os.urandom(2),
                data=os.urandom(random.randint(1, 128)),
            )
        )
        assert response.status.value == L2StatusEnum.UNKNOWN_REQ
