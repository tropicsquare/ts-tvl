import logging
from binascii import hexlify
from functools import singledispatch
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

import yaml
from cryptography.hazmat.primitives.asymmetric.ec import (
    EllipticCurvePrivateKey,
    SECP256R1,
)
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    load_der_private_key,
    load_der_public_key,
    load_pem_private_key,
    load_pem_public_key,
)
from cryptography.x509 import load_pem_x509_certificate
from pydantic import root_validator  # type: ignore
from pydantic import BaseModel, Extra, Field, FilePath, StrictBytes

from ..configuration_file_model import ModelConfigurationModel
from ..crypto.ecdsa import ecdsa_key_setup
from ..crypto.eddsa import eddsa_key_setup
from .logging_utils import LogDict, LogIter

DEFAULT_MODEL_CONFIG: Dict[Any, Any] = {
    "i_pairing_keys": {
        0: {
            "value": b"\x84/\xe3!\xa8$t\x0877\xff+\x9b\x88\xa2\xafBD-\xb0\xd8\xaa\xccm\xc6\x9e\x99S3D\xb2F"  # noqa E501
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


@singledispatch
def load_private_key(__value: Any) -> X25519PrivateKey:
    """Load a X25519 private key."""
    raise NotImplementedError(f"{type(__value)} not supported")


@load_private_key.register
def _(__value: bytes) -> X25519PrivateKey:
    return X25519PrivateKey.from_private_bytes(__value)


@load_private_key.register
def _(__value: Path) -> X25519PrivateKey:
    if __value.suffix == ".pem":
        private_key = load_pem_private_key(__value.read_bytes(), None)
    elif __value.suffix == ".der":
        private_key = load_der_private_key(__value.read_bytes(), None)
    else:
        raise TypeError("Private key not in DER nor PEM format")

    if not isinstance(private_key, (expected := X25519PrivateKey)):
        raise KeyTypeError("Private", type(private_key), expected)

    return private_key


@singledispatch
def load_public_key(__value: Any) -> X25519PublicKey:
    """Load a X25519 public key."""
    raise NotImplementedError(f"{type(__value)} not supported")


@load_public_key.register
def _(__value: bytes) -> X25519PublicKey:
    return X25519PublicKey.from_public_bytes(__value)


@load_public_key.register
def _(__value: Path) -> X25519PublicKey:
    if __value.suffix == ".pem":
        public_key = load_pem_public_key(__value.read_bytes(), None)
    elif __value.suffix == ".der":
        public_key = load_der_public_key(__value.read_bytes(), None)
    else:
        raise TypeError("Public key not in DER nor PEM format")

    if not isinstance(public_key, (expected := X25519PublicKey)):
        raise KeyTypeError("Public", type(public_key), expected)

    return public_key


@singledispatch
def load_certificate(__value: Any) -> bytes:
    """Load a x509 certificate in bytes format."""
    raise NotImplementedError(f"{type(__value)} not supported")


@load_certificate.register
def _(__value: bytes) -> bytes:
    return __value


@load_certificate.register
def _(__value: Path) -> bytes:
    if __value.suffix == ".pem":
        return load_pem_x509_certificate(__value.read_bytes()).public_bytes(
            Encoding.DER
        )
    if __value.suffix == ".der":
        return __value.read_bytes()
    raise TypeError("Certificate not in DER nor PEM format")


def _load_ecc_private_key(path: Path) -> Any:
    """Read and parse an ECC private key from a PEM/DER file.

    Wraps filesystem errors into ``ValueError`` so they surface as a clean
    Pydantic ``ValidationError`` instead of leaking a raw ``OSError`` out of the
    validator. Bad key material already raises ``ValueError`` from cryptography.
    """
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ValueError(
            f"Could not read ECC private key file '{path}': {exc}"
        ) from exc

    if path.suffix == ".pem":
        return load_pem_private_key(data, None)
    if path.suffix == ".der":
        return load_der_private_key(data, None)
    raise TypeError("ECC private key not in DER nor PEM format")


def _expand_ecc_private_key(path: Path, slot_data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a new slot dict with the derived ECC fields populated.

    For Ed25519 keys: computes s, prefix, a using eddsa_key_setup.
    For P256 keys: computes d, w, a using ecdsa_key_setup.
    The returned dict drops the ``private_key`` entry; the input ``slot_data``
    is left untouched (no in-place mutation of the caller's config).
    """
    key = _load_ecc_private_key(path)

    if isinstance(key, Ed25519PrivateKey):
        raw = key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
        s, prefix, a = eddsa_key_setup(raw)
        derived = {"s": s, "prefix": prefix, "a": a}
    elif isinstance(key, EllipticCurvePrivateKey) and isinstance(key.curve, SECP256R1):
        # ecdsa_key_setup expects a big-endian 32-byte private scalar
        raw = key.private_numbers().private_value.to_bytes(32, "big")
        d, w, a = ecdsa_key_setup(raw)
        derived = {"d": d, "w": w, "a": a}
    else:
        raise TypeError(f"Unsupported ECC key type for r_ecc_keys: {type(key)}")

    return {**{k: v for k, v in slot_data.items() if k != "private_key"}, **derived}


class ConfigurationModel(BaseModel, extra=Extra.allow):
    """Pydantic model to validate the configuration file"""

    filepath: FilePath = Field(exclude=True)
    s_t_priv: Union[StrictBytes, FilePath]
    s_t_pub: Optional[Union[StrictBytes, FilePath]]
    x509_certificate: Union[StrictBytes, FilePath]

    @root_validator(pre=True)  # type: ignore
    def set_paths_to_absolute(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        config_dir = values["filepath"].parent

        def _set(name: str) -> None:
            if isinstance(value := values.get(name), str):
                values[name] = config_dir / value

        _set("s_t_priv")
        _set("s_t_pub")
        _set("x509_certificate")

        # resolve r_ecc_keys private_key paths into new slot dicts (no in-place mutation)
        if isinstance(r_ecc_keys := values.get("r_ecc_keys"), dict):
            values["r_ecc_keys"] = {
                slot: (
                    {**slot_data, "private_key": config_dir / slot_data["private_key"]}
                    if isinstance(slot_data, dict)
                    and isinstance(slot_data.get("private_key"), str)
                    else slot_data
                )
                for slot, slot_data in r_ecc_keys.items()
            }

        return values

    @root_validator  # type: ignore
    def process_values(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # process public key
        if (s_t_pub := values.get("s_t_pub")) is not None:
            values["s_t_pub"] = load_public_key(s_t_pub).public_bytes_raw()

        # process private key
        if (s_t_priv := values.get("s_t_priv")) is not None:
            private_key = load_private_key(s_t_priv)
            values["s_t_priv"] = private_key.private_bytes_raw()

            # define tropic public key if not defined
            if "s_t_pub" not in values:
                values["s_t_pub"] = private_key.public_key().public_bytes_raw()

        # process certificate
        if (cert := values.get("x509_certificate")) is not None:
            values["x509_certificate"] = load_certificate(cert)

        # expand r_ecc_keys private_key shortcuts into derived fields
        if isinstance(r_ecc_keys := values.get("r_ecc_keys"), dict):
            values["r_ecc_keys"] = {
                slot: (
                    _expand_ecc_private_key(pk, slot_data)
                    if isinstance(slot_data, dict)
                    and isinstance(pk := slot_data.get("private_key"), Path)
                    else slot_data
                )
                for slot, slot_data in r_ecc_keys.items()
            }

        return values


def _open_yaml_file(filepath: Path) -> Dict[Any, Any]:
    with open(filepath, "r") as fd:
        return yaml.safe_load(fd)


def _write_to_yaml_file(filepath: Path, cfg: Dict[Any, Any]) -> None:
    with open(filepath, "w") as fd:
        yaml.dump(cfg, fd)


def _format(config: Dict[Any, Any]) -> Dict[Any, Any]:
    formatted_config: Dict[Any, Any] = {}
    for k, v in config.items():
        if isinstance(v, dict):
            formatted_config[k] = _format(v)  # type: ignore
        elif isinstance(v, bytes):
            formatted_config[k] = hexlify(v)
        else:
            formatted_config[k] = v
    return formatted_config


def load_configuration(
    filepath: Optional[Path],
    logger: logging.Logger,
    *,
    load_fn: Callable[[Path], Dict[Any, Any]] = _open_yaml_file,
) -> Dict[Any, Any]:
    if filepath is None:
        config: Dict[Any, Any] = {}

    else:
        logger.info("Loading target configuration from %s.", filepath)
        config = load_fn(filepath)
        config["filepath"] = filepath.absolute()
        logger.debug("Configuration from file:%s", LogDict(config, fn=_format))
        # Checking file content
        config = ConfigurationModel.parse_obj(config).dict()

    # Merging file configuration with default configuration
    config = merge_dicts(DEFAULT_MODEL_CONFIG, config)
    logger.debug("Configuration after merge:%s", LogDict(config, fn=_format))

    # Checking configuration
    config = ModelConfigurationModel.parse_obj(config).dict(exclude_none=True)
    logger.info(
        "Target Configuration loaded and validated:%s", LogDict(config, fn=_format)
    )
    logger.debug("STPUB[] = {%s};", LogIter(config["s_t_pub"], "%#04x"))
    return config


def dump_configuration(
    filepath: Path,
    cfg: Dict[Any, Any],
    logger: logging.Logger,
    *,
    dump_fn: Callable[[Path, Dict[Any, Any]], None] = _write_to_yaml_file,
) -> None:
    dump_fn(filepath, cfg)
    logger.debug("Target configuration dumped to %s", filepath)
