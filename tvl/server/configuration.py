import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    load_der_private_key,
    load_der_public_key,
    load_pem_private_key,
    load_pem_public_key,
)
from cryptography.x509 import load_der_x509_certificate, load_pem_x509_certificate
from pydantic import root_validator  # type: ignore
from pydantic import BaseModel, Extra, FilePath, StrictBytes

from ..configuration_file_model import ModelConfigurationModel
from .logging_utils import LogDict, LogIter

# TODO temporary solution, to be defined another way when flow is mature
DEFAULT_MODEL_CONFIG = {
    "i_pairing_keys": {
        0: {
            "value": b"\x83\xc36<\xff'G\xb7\xf7\xeb\x19\x85\x17c\x1aqTv\xb4\xfe\"F\x01E\x89\xc3\xac\x11\x8b\xb8\x9eQ"  # noqa E501
        }
    },
    "s_t_priv": b"H\xb9/\x05\x0b\xfb\x82@\"\xec\xef{\xc5\xec\xbc\xa4R\xd3\xfd'p\xe8\xb5T\x9e\x93g)\xacx\xc4m",  # noqa E501
    "s_t_pub": b"\x07z\xad\x06\x0b\xbb8F-:\xa5.\x9e\xef\xe8\xfa\xa7\x84\x16\x9b,g;\xe0n\xf3\xfe\x1f\xd1\xc1\x93G",  # noqa E501
}


class KeyTypeError(TypeError):
    def __init__(self, key_type: str, type_: type, expected_type: type) -> None:
        super().__init__(f"{key_type} key type is not {expected_type}: {type_}")


def merge_dicts(*dcts: Dict[Any, Any]) -> Dict[Any, Any]:
    """Merge dictionaries, the first has the least priority."""

    def _combine_into(d: Dict[Any, Any], combined: Dict[Any, Any]) -> None:
        for k, v in d.items():
            if isinstance(v, dict):
                _combine_into(v, combined.setdefault(k, {}))  # type: ignore
            else:
                combined[k] = v

    result: Dict[Any, Any] = {}
    for dct in dcts:
        _combine_into(dct, result)
    return result


class ConfigurationModel(BaseModel, extra=Extra.allow):
    """Pydantic model to validate the configuration file"""

    s_t_priv: Union[StrictBytes, FilePath]
    s_t_pub: Optional[Union[StrictBytes, FilePath]]
    x509_certificate: Union[StrictBytes, FilePath]

    @root_validator  # type: ignore
    def process_values(cls, values: Dict[str, Union[bytes, Path]]):
        # process public key
        if (s_t_pub := values.get("s_t_pub")) is not None:
            if isinstance(s_t_pub, bytes):
                public_key = X25519PublicKey.from_public_bytes(s_t_pub)
            elif s_t_pub.suffix == ".pem":
                public_key = load_pem_public_key(s_t_pub.read_bytes())
            elif s_t_pub.suffix == ".der":
                public_key = load_der_public_key(s_t_pub.read_bytes())
            else:
                raise TypeError("Public key not in DER nor PEM format")

            if not isinstance(public_key, (expected := X25519PublicKey)):
                raise KeyTypeError("Public", type(public_key), expected)
            values["s_t_pub"] = public_key.public_bytes_raw()

        # process private key
        if (s_t_priv := values.get("s_t_priv")) is not None:
            if isinstance(s_t_priv, bytes):
                private_key = X25519PrivateKey.from_private_bytes(s_t_priv)
            elif s_t_priv.suffix == ".pem":
                private_key = load_pem_private_key(s_t_priv.read_bytes(), None)
            elif s_t_priv.suffix == ".der":
                private_key = load_der_private_key(s_t_priv.read_bytes(), None)
            else:
                raise TypeError("Private key not in DER nor PEM format")

            if not isinstance(private_key, (expected := X25519PrivateKey)):
                raise KeyTypeError("Private", type(private_key), expected)
            values["s_t_priv"] = private_key.private_bytes_raw()
            # define tropic public key if not defined
            if values.get("s_t_pub") is None:
                values["s_t_pub"] = private_key.public_key().public_bytes_raw()

        # process certificate
        if (cert := values.get("x509_certificate")) is not None:
            if isinstance(cert, Path):
                if cert.suffix == ".pem":
                    certificate = load_pem_x509_certificate(cert.read_bytes())
                elif cert.suffix == ".der":
                    certificate = load_der_x509_certificate(cert.read_bytes())
                else:
                    raise TypeError("Certificate not in DER nor PEM format")
                values["certificate"] = certificate.public_bytes(Encoding.DER)

        return values


@lru_cache
def _open_yaml_file(filepath: Path) -> Dict[Any, Any]:
    return yaml.safe_load(filepath.read_bytes())


def load_configuration(
    filepath: Optional[Path], logger: logging.Logger
) -> Dict[Any, Any]:
    if filepath is None:
        config: Dict[Any, Any] = {}

    else:
        logger.info("Loading target configuration from %s.", filepath)
        config = _open_yaml_file(filepath)
        logger.debug("Configuration:%s", LogDict(config))
        # Checking file content
        config = ConfigurationModel.parse_obj(config).dict()

    # Merging file configuration with default configuration
    config = merge_dicts(DEFAULT_MODEL_CONFIG, config)
    logger.debug("Configuration after merge:%s", LogDict(config))

    # Checking configuration
    config = ModelConfigurationModel.parse_obj(config).dict(exclude_none=True)
    logger.debug("Validated configuration:%s", LogDict(config))
    logger.debug("STPUB[] = {%s};", LogIter(config["s_t_pub"], "%#04x"))
    logger.info("Target configuration loaded and validated.")
    return config
