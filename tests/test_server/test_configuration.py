import logging
from pathlib import Path
from typing import Any, Dict

import pytest
from cryptography.hazmat.primitives.asymmetric.ec import (
    SECP256R1,
    derive_private_key,
    generate_private_key,
)
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)
from pydantic.v1 import ValidationError

from tests.test_crypto.test_ecdsa import PRIV_KEY as _RFC6979_PRIV_KEY
from tests.test_crypto.test_ecdsa import UX as _RFC6979_UX
from tests.test_crypto.test_ecdsa import UY as _RFC6979_UY
from tvl.crypto.ecdsa import ecdsa_key_setup
from tvl.crypto.eddsa import eddsa_key_setup
from tvl.crypto.tmac import tmac
from tvl.server.configuration import load_configuration

# 32 bytes of X25519 private key used as s_t_priv in test configs
_S_T_PRIV = bytes(range(32))
_S_T_PUB = (
    X25519PrivateKey.from_private_bytes(_S_T_PRIV).public_key().public_bytes_raw()
)
_X509_CERT = b"\x00" * 32  # minimal placeholder cert bytes

LOG = logging.getLogger(__name__)


def _write_pem(path: Path, key) -> None:
    path.write_bytes(
        key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    )


def _write_der(path: Path, key) -> None:
    path.write_bytes(
        key.private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())
    )


def _load_config(tmp_path: Path, extra: Dict[str, Any]) -> Dict[str, Any]:
    """Call load_configuration with a synthetic dict, using tmp_path as config dir."""
    config_data = {
        "s_t_priv": _S_T_PRIV,
        "s_t_pub": _S_T_PUB,
        "x509_certificate": _X509_CERT,
        **extra,
    }
    # ConfigurationModel.filepath is a FilePath — the file must exist on disk.
    fake_filepath = tmp_path / "config.yml"
    fake_filepath.touch()
    return load_configuration(
        fake_filepath,
        LOG,
        load_fn=lambda _: config_data,
    )


# ---------------------------------------------------------------------------
# Test 1: Ed25519 PEM → s / prefix / a are expanded correctly
# ---------------------------------------------------------------------------


def test_r_ecc_keys_ed25519_pem(tmp_path: Path) -> None:
    key = Ed25519PrivateKey.generate()
    _write_pem(tmp_path / "sign.pem", key)

    raw = key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    expected_s, expected_prefix, expected_a = eddsa_key_setup(raw)

    result = _load_config(
        tmp_path,
        {"r_ecc_keys": {0: {"private_key": "sign.pem", "origin": 2}}},
    )

    slot = result["r_ecc_keys"][0]
    assert slot["s"] == expected_s
    assert slot["prefix"] == expected_prefix
    assert slot["a"] == expected_a
    assert "private_key" not in slot


# ---------------------------------------------------------------------------
# Test 2: P256 PEM → d / w / a are expanded correctly
# ---------------------------------------------------------------------------


def test_r_ecc_keys_p256_pem(tmp_path: Path) -> None:
    key = generate_private_key(SECP256R1())
    _write_pem(tmp_path / "sign.pem", key)

    # Ground truth derived independently of ecdsa_key_setup (the function under
    # test), so a byte-order regression in the implementation is actually
    # caught instead of the test just agreeing with itself.
    expected_d = key.private_numbers().private_value.to_bytes(32, "big")
    expected_w = tmac(expected_d, b"", b"\x0A")
    expected_a = key.public_key().public_bytes(
        Encoding.X962, PublicFormat.UncompressedPoint
    )[1:]

    result = _load_config(
        tmp_path,
        {"r_ecc_keys": {0: {"private_key": "sign.pem", "origin": 2}}},
    )

    slot = result["r_ecc_keys"][0]
    assert slot["d"] == expected_d
    assert slot["w"] == expected_w
    assert slot["a"] == expected_a
    assert "private_key" not in slot


# ---------------------------------------------------------------------------
# Test 3: Ed25519 DER format works the same way
# ---------------------------------------------------------------------------


def test_r_ecc_keys_ed25519_der(tmp_path: Path) -> None:
    key = Ed25519PrivateKey.generate()
    _write_der(tmp_path / "sign.der", key)

    raw = key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    expected_s, expected_prefix, expected_a = eddsa_key_setup(raw)

    result = _load_config(
        tmp_path,
        {"r_ecc_keys": {0: {"private_key": "sign.der", "origin": 2}}},
    )

    slot = result["r_ecc_keys"][0]
    assert slot["s"] == expected_s
    assert slot["prefix"] == expected_prefix
    assert slot["a"] == expected_a


# ---------------------------------------------------------------------------
# Test 4: Relative path is resolved relative to the config file's directory
# ---------------------------------------------------------------------------


def test_r_ecc_keys_relative_path_resolved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    key = Ed25519PrivateKey.generate()
    _write_pem(tmp_path / "sign.pem", key)

    # Run from a directory different from tmp_path so a naive relative-path join
    # (relative to cwd instead of the config file) would fail to find the key.
    other_dir = tmp_path / "elsewhere"
    other_dir.mkdir()
    monkeypatch.chdir(other_dir)

    result = _load_config(
        tmp_path,
        {"r_ecc_keys": {0: {"private_key": "sign.pem", "origin": 2}}},
    )

    assert "s" in result["r_ecc_keys"][0]


# ---------------------------------------------------------------------------
# Test 5: Backward-compat — explicit s / prefix / a still works unchanged
# ---------------------------------------------------------------------------


def test_r_ecc_keys_explicit_fields_still_work(tmp_path: Path) -> None:
    key = Ed25519PrivateKey.generate()
    raw = key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    s, prefix, a = eddsa_key_setup(raw)

    result = _load_config(
        tmp_path,
        {"r_ecc_keys": {0: {"s": s, "prefix": prefix, "a": a, "origin": 2}}},
    )

    slot = result["r_ecc_keys"][0]
    assert slot["s"] == s
    assert slot["prefix"] == prefix
    assert slot["a"] == a
    assert "private_key" not in slot


# ---------------------------------------------------------------------------
# Test 6: Unsupported key type (X25519) raises TypeError
# ---------------------------------------------------------------------------


def test_r_ecc_keys_unsupported_key_type_raises(tmp_path: Path) -> None:
    key = X25519PrivateKey.generate()
    _write_pem(tmp_path / "sign.pem", key)

    # The TypeError is wrapped by Pydantic into a ValidationError
    with pytest.raises(ValidationError, match="Unsupported ECC key type"):
        _load_config(
            tmp_path,
            {"r_ecc_keys": {0: {"private_key": "sign.pem", "origin": 2}}},
        )


# ---------------------------------------------------------------------------
# Test 7: Multiple slots — one via private_key, one via explicit fields
# ---------------------------------------------------------------------------


def test_r_ecc_keys_mixed_slots(tmp_path: Path) -> None:
    ed_key = Ed25519PrivateKey.generate()
    _write_pem(tmp_path / "sign.pem", ed_key)
    ed_raw = ed_key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    expected_s, expected_prefix, expected_a = eddsa_key_setup(ed_raw)

    p256_key = generate_private_key(SECP256R1())
    p256_raw = p256_key.private_numbers().private_value.to_bytes(32, "little")
    exp_d, exp_w, exp_a = ecdsa_key_setup(p256_raw)

    result = _load_config(
        tmp_path,
        {
            "r_ecc_keys": {
                0: {"private_key": "sign.pem", "origin": 2},
                1: {"d": exp_d, "w": exp_w, "a": exp_a, "origin": 2},
            }
        },
    )

    slot0 = result["r_ecc_keys"][0]
    assert slot0["s"] == expected_s
    assert slot0["prefix"] == expected_prefix
    assert slot0["a"] == expected_a

    slot1 = result["r_ecc_keys"][1]
    assert slot1["d"] == exp_d
    assert slot1["w"] == exp_w
    assert slot1["a"] == exp_a


# ---------------------------------------------------------------------------
# Test 8: Missing key file raises a clean ValidationError, not a raw OSError
# ---------------------------------------------------------------------------


def test_r_ecc_keys_missing_file_raises(tmp_path: Path) -> None:
    # No key file is written, so the referenced path does not exist.
    with pytest.raises(ValidationError, match="Could not read ECC private key file"):
        _load_config(
            tmp_path,
            {"r_ecc_keys": {0: {"private_key": "does_not_exist.pem", "origin": 2}}},
        )


# ---------------------------------------------------------------------------
# Test 9: Expansion does not mutate the caller's input slot dict
# ---------------------------------------------------------------------------


def test_r_ecc_keys_input_dict_not_mutated(tmp_path: Path) -> None:
    key = Ed25519PrivateKey.generate()
    _write_pem(tmp_path / "sign.pem", key)

    slot = {"private_key": "sign.pem", "origin": 2}
    result = _load_config(tmp_path, {"r_ecc_keys": {0: slot}})

    # The loaded result is expanded ...
    assert {"s", "prefix", "a"} <= result["r_ecc_keys"][0].keys()
    # ... but the original input dict is left untouched.
    assert slot == {"private_key": "sign.pem", "origin": 2}


# ---------------------------------------------------------------------------
# Test 10: P256 PEM loaded from a known-answer (RFC 6979) test vector
# ---------------------------------------------------------------------------


def test_r_ecc_keys_p256_pem_known_answer_vector(tmp_path: Path) -> None:
    """Pin against RFC 6979 Appendix A.2.5, not a value derived at test time.

    Same vector as tests/test_crypto/test_ecdsa.py::test_standard_ecdsa_key_setup.
    A wrong byte order in the PEM-loading path (see configuration.py) reduces the
    scalar to a different value mod q, so this fails loudly against the fixed
    expected public key instead of silently agreeing with itself.
    """
    key = derive_private_key(int.from_bytes(_RFC6979_PRIV_KEY, "big"), SECP256R1())
    _write_pem(tmp_path / "sign.pem", key)

    result = _load_config(
        tmp_path,
        {"r_ecc_keys": {0: {"private_key": "sign.pem", "origin": 2}}},
    )

    slot = result["r_ecc_keys"][0]
    assert slot["d"] == _RFC6979_PRIV_KEY
    assert slot["w"] == tmac(_RFC6979_PRIV_KEY, b"", b"\x0A")
    assert slot["a"] == _RFC6979_UX + _RFC6979_UY
    assert "private_key" not in slot
