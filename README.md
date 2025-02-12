# TROPIC Verification Library

The TROPIC Verification Library (TVL) is a [Python](https://www.python.org/)
package for evaluating TROPIC01 functionalities.
It is written from the TROPIC01 datasheet and API documents.

## Installation

### Download the TVL package

The TVL wheel file is automatically packaged by Github actions.
It is available at
[https://github.com/tropicsquare/ts-tvl/actions/workflows/test_and_build.yaml](https://github.com/tropicsquare/ts-tvl/actions/workflows/test_and_build.yaml).
To download it, click on the latest workflow run then scroll down
to the section `Artifacts` and download the `ts-tvl-package` artifact.

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

### Create a Python virtual environment

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
pip install tvl-0.10.1-py3-none-any.whl
```

# Model server

Along with the TVL comes a command-line tool that exposes a `Tropic01Model`
behind a TCP/IP server or a serial port.

Once the TVL is installed and the virtual environemnt activated (see above)
the model server is available in the terminal:

```shell
model_server tcp
```

For more information about the model server tool, type:

```shell
model_server tcp --help
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
model_server tcp --configuration=model_config.yml
```
