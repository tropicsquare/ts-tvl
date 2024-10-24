# TROPIC Verification Library

The TROPIC Verification Library (TVL) is a [Python](https://www.python.org/)
package for evaluating TROPIC01 functionalities.
It is written from the TROPIC01 datasheet and API documents.

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

The TVL is automatically packaged by github actions. It is available at
[https://github.com/tropicsquare/ts-tvl/actions/workflows/test_and_build.yaml](https://github.com/tropicsquare/ts-tvl/actions/workflows/test_and_build.yaml).
To download it, click on the latest workflow run then scroll down
to the section `Artifacts` and download the `ts-tvl-package` artifact.

The installation of the TVL:

```shell
pip install tvl-0.9.0-py3-none-any.whl
```

## How to use

1. instantiate and configure a TROPIC01 target
2. instantiate the `Host` and link to the target
3. create a request or a command
4. send the request or command to the target via the `Host` instance
5. repeat steps 3. and 4.

## A basic example: issue a GetInfo request

This example can also be found in
[`examples/example_01_get_info_request.py`](examples/example_01_get_info_request.py)

```python
from tvl.api.l2_api import TsL2GetInfoRequest
from tvl.host.host import Host
from tvl.logging import setup_logging
from tvl.targets.model.tropic01_model import Tropic01Model

# Configure logging
setup_logging()

# Instantiate the target (in this case, `Tropic01Model`)
model = Tropic01Model()

# Instantiate the `Host`
host = Host(target=model)

# Create a message (in this case `TsL2GetInfoRequest`)
request = TsL2GetInfoRequest(object_id=1, block_index=0)
print(request)
# > TsL2GetInfoRequest<(id=AUTO, length=AUTO, object_id=01, block_index=00, crc=AUTO)

# Send the request and then receive the response
response = host.send_request(request)

print(response)
# > TsL2GetInfoReqResponse<(status=01, length=07, object=[63, 68, 69, 70, 5f, 69, 64], crc=f253)
```

More examples in the [`examples`](examples/) directory.

# Model server

Along with the TVL comes a command-line tool that exposes a `Tropic01Model`
behind a TCP/IP server or a serial port.

Once the TVL package is installed, the model server is available in the terminal.
For example:

```shell
model_server --help
```

For more information about the TCP/IP server:

```shell
model_server tcp --help
```

For more information about the serial port server:

```shell
model_server serial --help
```

## Configuration file

It is possible (and recommended) to provide a [yaml](https://yaml.org/)
configuration file to the model_server to configure the `Tropic01Model`.
This file is parsed by model_server using
[pydantic](https://pypi.org/project/pydantic/1.10.13/).

For more information about the configuration file syntax, have a look
[here](tvl/server/configuration.py) and [here](tvl/configuration_file_model.py).

This repository offers the user a basic configuration file available
[here](tvl/server/model_config/).
To use it, just copy the content of the directory to your working directory and
specify the option `--configuration` when running the model server.

```shell
# in the case the TCP/ interface is used
model_server tcp --configuration=model_config.yml
# or
model_server tcp -c model_config.yml
```