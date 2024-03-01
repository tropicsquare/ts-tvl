#!/usr/bin/env python3

# ######################################################################################
# This test sends a GetInfo request to the Tropic01Model and prints the response.
# ######################################################################################

from tvl.api.l2_api import TsL2GetInfoReqRequest
from tvl.host.host import Host
from tvl.logging_utils import setup_logging
from tvl.targets.model.tropic01_model import Tropic01Model

# Configure logging
setup_logging()

# Instantiate the target (in this case, `Tropic01Model`)
model = Tropic01Model()

# Instantiate the `Host`
host = Host(target=model)

# Create a message (in this case `TsL2GetInfoReqRequest`)
request = TsL2GetInfoReqRequest(object_id=1, block_index=0)
print(request)
# > TsL2GetInfoReqRequest<(id=AUTO, length=AUTO, object_id=01, block_index=00, crc=AUTO)

# Send the request and then receive the response
response = host.send_request(request)

print(response)
# > TsL2GetInfoReqResponse<(status=01, length=07, object=[63, 68, 69, 70, 5f, 69, 64], crc=f253)
