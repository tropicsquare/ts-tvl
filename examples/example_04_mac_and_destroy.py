#!/usr/bin/env python3

# #############################################################################
# This example establishes a secure channel between the model and the host.
# It then performs a Mac-and-Destroy operation.
# #############################################################################

import os
from pathlib import Path
from random import randint

from tvl.api.l2_api import TsL2HandshakeReqRequest, TsL2HandshakeReqResponse
from tvl.api.l3_api import (
    TsL3MacAndDestroyCommand,
    TsL3MacAndDestroyResult,
    TsL3PingCommand,
    TsL3PingResult,
)
from tvl.configuration_file_model import load_configuration_file
from tvl.constants import L2StatusEnum, L3ResultFieldEnum
from tvl.host.host import Host
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

# Establish a secure channel between the model and the host:
# send a Handshake request
handshake_request = TsL2HandshakeReqRequest(
    e_hpub=host.session.create_handshake_request(),
    pkey_index=host.pairing_key_index,
)

handshake_response = host.send_request(handshake_request)

assert isinstance(handshake_response, TsL2HandshakeReqResponse)
assert handshake_response.status.value == L2StatusEnum.REQ_OK

# Check the secure channel session is well established: send a Ping command
ping_command_data_in = os.urandom(randint(1, 32))

ping_command = TsL3PingCommand(data_in=ping_command_data_in)
ping_result = host.send_command(ping_command)

assert isinstance(ping_result, TsL3PingResult)
assert ping_result.result.value == L3ResultFieldEnum.OK
assert ping_result.data_out.value == ping_command.data_in.value
assert ping_result.data_out.to_bytes() == ping_command_data_in

# Perform the Mac-and-Destroy operation
macandd_command_slot = randint(1, 128)
macandd_command_data_in = os.urandom(32)

macandd_command = TsL3MacAndDestroyCommand(
    slot=macandd_command_slot, padding=[], data_in=macandd_command_data_in
)
macandd_result = host.send_command(macandd_command)

assert isinstance(macandd_result, TsL3MacAndDestroyResult)
assert macandd_result.result.value == L3ResultFieldEnum.OK
