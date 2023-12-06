# TROPIC Verification Library

The TROPIC Verification Library (TVL) is a [Python](https://www.python.org/)
package for evaluating TROPIC01 functionalities.
It is written from the TROPIC01
[datasheet](https://tropic-gitlab.corp.sldev.cz/internal/tropic01/tassic/-/jobs/artifacts/master/file/public/tropic01_datasheet.pdf?job=pages)
and
[API](https://tropic-gitlab.corp.sldev.cz/internal/tropic01/tassic/-/jobs/artifacts/master/file/public/tropic01_user_api.pdf?job=pages)
documents.

Three main components are defined in the TVL:
- targets: interfaces to the TROPIC01 implementations
- `Host`: abstraction of the Host MCU, providing utilities to communicate with a target
- messages: classes for modelling the data exchanged with the targets.

## Targets
The TVL provides a set of classes to communicate with the different implementations
of TROPIC01, referred to as targets, namely:

- `Tropic01Model`: the reference model, written in Python

More on TROPIC01 targets [here](./tvl/targets/README.md).

## Host
The `Host` class intends to provide a user-friendly way to communicate with a
target. It abstracts the low-level communication details, thus allowing the user
to focus on the content of the messages sent to the target.

More on TROPIC01 host [here](./tvl/host/README.md).

## Messages
The messages exchanged between the host and the target are implemented as Python
classes. These classes are defined based on the API (see above).
They abstract the way the messages are created an perform several low-level
operations.

More on messages [here](./tvl/messages/README.md).

## Installing

To use the TVL, install it in your Python environment.
A good practice consists of creating a Python virtual environment beforehand:

```shell
python3.8 -m venv myvenv
source myvenv/bin/activate
```

The installation of the TVL:

```shell
pip install tvl-1.0.0-py3-none-any.whl
```

## How to use

1. instantiate and configure a TROPIC01 target
2. instantiate the `Host` and link to the target
3. create a request or a command
4. send the request or command to the target via the `Host` instance
5. repeat steps 3. and 4.

## Simple example: L2-level communication

```python
from tvl.host.host import Host
from tvl.targets.model.tropic01_model import Tropic01Model
from tvl.api.l2_api import TsL2GetInfoReqRequest

# Instantiation of a target, here the `Tropic01Model`
model = Tropic01Model()
# Instantiation of the `Host`
host = Host(target=model)

# Creation of a message, here `TsL2GetInfoReqRequest`
request = TsL2GetInfoReqRequest(object_id=1, block_index=0)
print(request)
# > TsL2GetInfoReqRequest<(id=AUTO, length=AUTO, object_id=01, block_index=00, crc=AUTO)

# Sending of the request and reception of the response
response = host.send_request(request)

print(response)
# > TsL2GetInfoReqResponse<(status=01, length=07, object=[63, 68, 69, 70, 5f, 69, 64], crc=f253)
```

## More complete example: enabling L3-level communication

```python
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from tvl.host.host import Host, SessionError
from tvl.targets.model.tropic01_model import Tropic01Model
from tvl.constants import L2StatusEnum, L3ResultFieldEnum
from tvl.api.l2_api import TsL2HandshakeReqRequest, TsL2HandshakeReqResponse
from tvl.api.l3_api import TsL3PingCommand, TsL3PingResult
from tvl.logging import setup_logging

# Create X25519 keys to initialize the model and the host
HOST_PRIVATE_KEY = X25519PrivateKey.generate()
HOST_PRIVATE_KEY_BYTES = HOST_PRIVATE_KEY.private_bytes_raw()
HOST_PUBLIC_KEY_BYTES = HOST_PRIVATE_KEY.public_key().public_bytes_raw()

TROPIC_PRIVATE_KEY = X25519PrivateKey.generate()
TROPIC_PRIVATE_KEY_BYTES = TROPIC_PRIVATE_KEY.private_bytes_raw()
TROPIC_PUBLIC_KEY_BYTES = TROPIC_PRIVATE_KEY.public_key().public_bytes_raw()

PAIRING_KEY_INDEX = 1

# Configure logging (a dictionary can be used)
setup_logging()

# Instantiate model
model = Tropic01Model.from_dict(
    {
        "s_t_priv": TROPIC_PRIVATE_KEY_BYTES,
        "s_t_pub": TROPIC_PUBLIC_KEY_BYTES,
        "i_pairing_keys": {
            PAIRING_KEY_INDEX: {"value": HOST_PUBLIC_KEY_BYTES},
        },
    }
)

# Instantiate host
host = Host.from_dict(
    {
        "s_h_priv": HOST_PRIVATE_KEY_BYTES,
        "s_h_pub": HOST_PUBLIC_KEY_BYTES,
        "s_t_pub": TROPIC_PUBLIC_KEY_BYTES,
        "pairing_key_index": PAIRING_KEY_INDEX,
    }
# Set the model as being the host's target
).set_target(model)

# Secure channel is not yet established: send ping command to confirm
ping_command_data_in = b"deadbeef"

ping_command = TsL3PingCommand(data_in=ping_command_data_in)

try:
    ping_result = host.send_command(ping_command)
except SessionError as exc:
    print(exc)
    # > Cannot encrypt command: no valid session.
else:
    assert False, "SessionError should be raised"

# Establish secure channel between model and host: send handshake request
handshake_request = TsL2HandshakeReqRequest(
    e_hpub=host.session.create_handshake_request(),
    pkey_index=host.pairing_key_index,
)

handshake_response = host.send_request(handshake_request)

assert isinstance(handshake_response, TsL2HandshakeReqResponse)
assert handshake_response.status.value == L2StatusEnum.REQ_OK

# Test L3 layer communication: send ping command
ping_result = host.send_command(ping_command)

assert isinstance(ping_result, TsL3PingResult)
assert ping_result.result.value == L3ResultFieldEnum.OK
assert ping_result.data_out.value == ping_command.data_in.value
assert ping_result.data_out.to_bytes() == ping_command_data_in
```
