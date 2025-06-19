# TROPIC Verification Library

The TROPIC Verification Library (TVL) is a [Python](https://www.python.org/)
package used for evaluating [TROPIC01 chip](https://github.com/tropicsquare/TROPIC01) and offers a model with the chip behaviour.

For more information about TROPIC01 chip check out developers resources in [TROPIC01](https://github.com/tropicsquare/tropic01) repository.

## Installation

### Download the TVL Package

There are [releases](https://github.com/tropicsquare/ts-tvl/releases) for every version of TVL,
containing the Python wheel file. Download one of the releases (the latest one is recommended) and
follow the steps below.

> The TVL wheel file is also generated on every push to the master branch and uploaded as an artifact.
> This wheel version is usually used by developers and does not always guarantee full functionality - for
> guaranteed stability, use the [releases](https://github.com/tropicsquare/ts-tvl/releases) versions instead. 
>
> Unreleased versions are available [here](https://github.com/tropicsquare/ts-tvl/actions/workflows/test_and_build.yaml). To download it, click on the latest workflow run then scroll down to the section
`Artifacts` and download the `ts-tvl-package` artifact.

### Install Python3.8

The TVL has been developed using Python 3.8. Other versions of Python might
support the TVL but this has not been checked in TropicSquare.

First, check whether `python3.8` is present on your machine:

```shell
python3.8 --version
```

If this command ends without an error, it means that `python3.8` is installed
and you can proceed to the installation of the Python virtual environment.

Otherwise, install `python3.8` as follows if you have a Debian-like OS (Ubuntu for example):

```shell
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.8 python3.8-venv -y
```

> If your OS is different, you may need to run other commands to install Python 3.8
> on your machine. Follow your machine's OS recommendations for doing so.

### Create a Python Virtual Environment

To use the TVL, install it in a Python virtual environment beforehand.

```shell
mkdir myproject
cd myproject

python3.8 -m venv myvenv
source myvenv/bin/activate
```

> The virtual environment will deactivate if you type the comand `deactivate`
> or if you close your shell. If you want to activate the virtual environment
> again, call `source myvenv/bin/activate`.

### Install the TVL

The installation of the TVL is done like so:

```shell
pip install <path to the TVL wheel file>
```

Example:

```shell
pip install tvl-1.0-py3-none-any.whl
```

# Model Server

Along with the TVL comes a command-line tool that exposes a `Tropic01Model`
behind a TCP/IP server or a serial port.

Once the TVL is installed and the virtual environment activated (see above),
the `model_server` is available in the terminal:

```shell
model_server tcp
```

For more information about the `model_server` tool, type:

```shell
model_server tcp --help
```
## Examples
See [available examples](examples/) for the functionality demonstration. They can be executed as:
```shell
./example_01_get_info_request.py
```

## Model Configuration

It is possible (and recommended) to provide a [yaml](https://yaml.org/)
configuration file to the `model_server` to configure the `Tropic01Model`.
This file is parsed by `model_server` using
[pydantic](https://pypi.org/project/pydantic/1.10.13/).

Available configuration variables for the Model can be seen [here](https://github.com/tropicsquare/ts-tvl/blob/e3ed3c93100e8fe316efc1582071a9da793fa77a/tvl/configuration_file_model.py#L40C1-L60C42). Keys and certificates can be passed as strings in base64 encoding or as files in PEM or DER format.

An example configuration can be found [here](model_configs/example_config/example_config.yml). Configurations are passed to the `model_server` as:

```shell
model_server tcp --configuration=config.yml
```
where `config.yml` is the path to the configuration file.

# TVL Documentation
A detailed documentation about TVL can be found [here](tvl/README.md).

# License

See the [LICENSE.md](LICENSE.md) file in the root of this repository or consult license information at [Tropic Square website](http:/tropicsquare.com/license).
