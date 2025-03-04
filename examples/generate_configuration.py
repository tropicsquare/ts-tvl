#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
from random import randrange
from typing import Any, Dict

import yaml
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from tvl.configuration_file_model import ConfigurationFileModel


def get_filename() -> Path:
    parser = ArgumentParser(
        f"./{Path(__file__).name}",
        description="Generate the configuration file for the examples.",
    )
    parser.add_argument(
        "-f",
        "--filename",
        default="conf.yml",
        help="Output file. Defaults to %(default)s",
    )
    return Path(__file__).parent / parser.parse_args().filename


def generate_configuration() -> Dict[str, Any]:
    # Host keys
    host_private_keys = [X25519PrivateKey.generate() for _ in range(4)]
    host_private_key_bytes = [key.private_bytes_raw() for key in host_private_keys]
    host_public_key_bytes = [
        key.public_key().public_bytes_raw() for key in host_private_keys
    ]

    # Model keys
    tropic_private_key = X25519PrivateKey.generate()
    tropic_private_key_bytes = tropic_private_key.private_bytes_raw()
    tropic_public_key_bytes = tropic_private_key.public_key().public_bytes_raw()

    # Four pairing key indices are available
    pairing_key_index = randrange(4)

    configuration = {  # type: ignore
        "host": {
            "s_h_priv": host_private_key_bytes,
            "s_h_pub": host_public_key_bytes,
            "s_t_pub": tropic_public_key_bytes,
            "pairing_key_index": pairing_key_index,
        },
        "model": {
            "s_t_priv": tropic_private_key_bytes,
            "s_t_pub": tropic_public_key_bytes,
            "i_pairing_keys": {
                pairing_key_index: {
                    "value": host_public_key_bytes[pairing_key_index],
                },
            },
        },
    }

    # Validate the configuration
    ConfigurationFileModel.validate(configuration)
    return configuration  # type: ignore


def main():
    filename = get_filename()
    configuration = generate_configuration()

    with open(filename, "w") as fd:
        yaml.dump(configuration, fd)


if __name__ == "__main__":
    main()
