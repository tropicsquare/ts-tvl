#!/usr/bin/env python3

# ######################################################################################
# This test establish a secure channel between the Tropic01Model and the Host.
# The messages are created manually, i.e. without the classes offered by the TVL.
# ######################################################################################

from pathlib import Path

from tvl.api.l2_api import L2Enum
from tvl.api.l3_api import L3Enum
from tvl.configuration_file_model import load_configuration_file
from tvl.constants import L2StatusEnum, L3ResultFieldEnum
from tvl.host.host import Host, SessionError
from tvl.logging_utils import setup_logging
from tvl.messages.l2_messages import crc16
from tvl.targets.model.tropic01_model import Tropic01Model


def crc(data: bytes) -> bytes:
    return crc16(data).to_bytes(2, byteorder="little")


# Load the configuration of the model and the host
configuration = load_configuration_file(Path(__file__).parent / "conf.yml")

# pairing key index
pairing_key_index: int = configuration["host"]["pairing_key_index"]
pairing_key_index_bytes = bytes([pairing_key_index])

# Configure logging
setup_logging()

# Instantiate the model
model = Tropic01Model.from_dict(configuration["model"])

# Instantiate the host
host = Host.from_dict(configuration["host"]).set_target(model)

# Secure channel is not yet established: Send a Ping command to confirm
ping_command_data_in = b"deadbeef"

# Create command field by field
ping_command_bytes = bytes([L3Enum.PING]) + ping_command_data_in  # CMD_ID  # CMD_DATA

# A SessionError should be raised
try:
    ping_result_bytes = host.send_command(ping_command_bytes)
except SessionError as exc:
    print(exc)
    # > Cannot encrypt command: no valid session
else:
    assert False, "SessionError should be raised"

# Establish a secure channel between the model and the host: Send a Handshake request
e_hpub = host.session.create_handshake_request()

# Create request field by field
handshake_request_bytes = (
    bytes([L2Enum.HANDSHAKE])  # REQ_ID
    + bytes([len(e_hpub) + len(pairing_key_index_bytes)])  # REQ_LEN
    + e_hpub  # e_hpub field of REQ_DATA
    + pairing_key_index_bytes  # pkey_index field of REQ_DATA
)
handshake_request_bytes += crc(handshake_request_bytes)  # REQ_CRC

handshake_response_bytes = host.send_request(handshake_request_bytes)

assert handshake_response_bytes[0] == L2StatusEnum.REQ_OK  # check STATUS

# Check the secure channel session is well established: Send a Ping command
ping_result_bytes = host.send_command(ping_command_bytes)

assert ping_result_bytes[0] == L3ResultFieldEnum.OK  # check RESULT
assert ping_result_bytes[1:] == ping_command_data_in  # check RES_DATA
