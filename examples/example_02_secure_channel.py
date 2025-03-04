#!/usr/bin/env python3

# ######################################################################################
# This test establish a secure channel between the Tropic01Model and the Host.
# ######################################################################################

from pathlib import Path

from tvl.api.l2_api import TsL2HandshakeRequest, TsL2HandshakeResponse
from tvl.api.l3_api import TsL3PingCommand, TsL3PingResult
from tvl.configuration_file_model import load_configuration_file
from tvl.constants import L2StatusEnum, L3ResultFieldEnum
from tvl.host.host import Host, SessionError
from tvl.logging_utils import setup_logging
from tvl.targets.model.tropic01_model import Tropic01Model

# Load the configuration of the model and the host
configuration = load_configuration_file(Path(__file__).parent / "conf.yml")

# Configure logging
setup_logging()

# Instantiate the model
model = Tropic01Model.from_dict(configuration["model"])

# Instantiate the host
host = Host.from_dict(configuration["host"]).set_target(model)

# Secure channel is not yet established: Send a Ping command to confirm
ping_command_data_in = b"deadbeef"

ping_command = TsL3PingCommand(data_in=ping_command_data_in)

# A SessionError should be raised
try:
    ping_result = host.send_command(ping_command)
except SessionError as exc:
    print(exc)
    # > Cannot encrypt command: no valid session
else:
    assert False, "SessionError should be raised"

# Establish a secure channel between the model and the host: Send a Handshake request
handshake_request = TsL2HandshakeRequest(
    e_hpub=host.session.create_handshake_request(),
    pkey_index=host.pairing_key_index,
)

handshake_response = host.send_request(handshake_request)

assert isinstance(handshake_response, TsL2HandshakeResponse)
assert handshake_response.status.value == L2StatusEnum.REQ_OK

# Check the secure channel session is well established: Send a Ping command
ping_result = host.send_command(ping_command)

assert isinstance(ping_result, TsL3PingResult)
assert ping_result.result.value == L3ResultFieldEnum.OK
assert ping_result.data_out.value == ping_command.data_in.value
assert ping_result.data_out.to_bytes() == ping_command_data_in
