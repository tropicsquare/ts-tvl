from typing import Tuple

from Crypto.PublicKey.ECC import EccPoint
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from .tmac import tmac


class P256_PARAMETERS:
    G = [
        0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
        0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5,
    ]
    """Base point generating the underlying subgroup (X,Y coordinate)"""
    q = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    """Order of the subgroup generated by G"""
    h = 0x1
    """Cofactor of the subgroup generated by G"""


ECDSA_G = EccPoint(*P256_PARAMETERS.G, curve="secp256r1")
ECDSA_KEY_SIZE = 64


class SignatureError(Exception):
    pass


def _to_int(__bytes: bytes, /) -> int:
    return int.from_bytes(__bytes, byteorder="big")


def _to_bytes(__int: int, /, *, size: int) -> bytes:
    return __int.to_bytes(size, byteorder="big")


def _assert_not_zero(__n: int, /) -> None:
    if __n == 0:
        raise SignatureError(
            "Signing algorithm calculated a zero value. This is a fatal error."
        )


def is_private_key_valid(key: bytes) -> bool:
    return 1 <= _to_int(key) <= P256_PARAMETERS.q - 1


def ecdsa_key_setup(k: bytes) -> Tuple[bytes, bytes, bytes]:
    """Setup a new ECDSA key.

    Args:
        k (bytes): private key

    Returns:
        private key 1, private key 2, public key
    """
    # For ECC_Generate SPECT uses 64 bytes of private_value to increase entropy
    k_reduce = _to_int(k) % P256_PARAMETERS.q
    private_key = ec.derive_private_key(k_reduce, ec.SECP256R1())

    d = _to_bytes(private_key.private_numbers().private_value, size=32)

    w = tmac(d, b"", b"\x0A")

    a = private_key.public_key().public_bytes(
        Encoding.X962, PublicFormat.UncompressedPoint
    )[1:]
    return d, w, a


def ecdsa_sign(d: bytes, w: bytes, z: bytes, h: bytes, n: bytes) -> Tuple[bytes, bytes]:
    """Sign a message's hash with the ECDSA algorithm.

    Args:
        d (bytes): private key 1
        w (bytes): private key 2
        z (bytes): the message's hash
        h (bytes): handshake hash
        n (bytes): nonce

    Returns:
        the signature (r, s)
    """
    return ecdsa_sign_second_part(*ecdsa_sign_first_part(d, w, z, h, n))


def ecdsa_sign_first_part(
    d: bytes, w: bytes, z: bytes, h: bytes, n: bytes
) -> Tuple[bytes, bytes, int]:
    """
    First part of the ECDSA signing algorithm.
    The computation of k is separated from the rest so the testing is easier.
    """
    k1 = tmac(w, h + n + z, b"\x0B")
    k2 = tmac(k1, b"", b"\x0B")
    k_int = _to_int(k2 + k1) % P256_PARAMETERS.q
    _assert_not_zero(k_int)
    return d, z, k_int


def ecdsa_sign_second_part(d: bytes, z: bytes, k_int: int) -> Tuple[bytes, bytes]:
    """
    Second part of the ECDSA signing algorithm.
    The computation of k is separated from the rest so the testing is easier.
    """
    g = ECDSA_G * k_int
    r_int = int(g.x) % P256_PARAMETERS.q
    _assert_not_zero(r_int)

    k_inv = pow(k_int, P256_PARAMETERS.q - 2, P256_PARAMETERS.q)
    d_int = _to_int(d)
    z_int = _to_int(z)
    s_int = k_inv * (z_int + (d_int * r_int)) % P256_PARAMETERS.q
    _assert_not_zero(s_int)

    r = _to_bytes(r_int, size=32)
    s = _to_bytes(s_int, size=32)
    return r, s
