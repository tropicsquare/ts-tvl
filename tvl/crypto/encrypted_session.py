from hashlib import sha256
from hmac import HMAC
from typing import Optional, Protocol, Tuple

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PROTOCOL_NAME = b"Noise_KK1_25519_AESGCM_SHA256\x00\x00\x00"

X25519_KEY_LEN = 32
"""Number of bytes of a X25519 key."""

MAX_NONCE = (1 << 32) - 1
"""Maximum value of the secure channel nonce."""

IV_LEN = 12
"""Length of AES-GCM initialization vector, aka nonce."""


class _RandomSource(Protocol):
    def urandom(self, size: int, /) -> bytes:
        ...


def hkdf(salt: bytes, input_keying_material: bytes) -> Tuple[bytes, bytes]:
    temp_key = HMAC(salt, input_keying_material, sha256).digest()
    output1 = HMAC(temp_key, b"\x01", sha256).digest()
    output2 = HMAC(temp_key, output1 + b"\x02", sha256).digest()
    return output1, output2


def encrypt(key: bytes, nonce: bytes, plaintext: bytes) -> bytes:
    return AESGCM(key).encrypt(nonce, plaintext, None)


def decrypt(key: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
    return AESGCM(key).decrypt(nonce, ciphertext, None)


class EncryptedSessionBase:
    """
    Implements the cryptographic operations of the secure channel that are
    common to the host and the Tropic chip.
    """

    def __init__(self, random_source: _RandomSource) -> None:
        """Initialize a new encrypted session.

        Args:
            random_source (_RandomSource): source of entropy for key generation
        """
        self.reset()
        self.random_source = random_source

    def reset(self) -> None:
        self.nonce_cmd = -1
        self.nonce_resp = -1
        self.k_cmd = b""
        self.k_resp = b""
        self.k_auth = b""
        self.handshake_hash = b""

    def execute_handshake(
        self,
        sh_key_index: int,  # static host pairing key index
        sh_public_key: bytes,  # static host pairing public key
        st_public_key: bytes,  # static Tropic public key
        eh_public_key: bytes,  # ephemeral host public key
        et_public_key: bytes,  # ephemeral Tropic public key
        secret_eh_et: bytes,  # ephemeral-host/ephemeral-Tropic shared secret
        secret_sh_et: bytes,  # static-host/ephemeral-Tropic shared secret
        secret_eh_st: bytes,  # ephemeral-host/static-Tropic shared secret
    ) -> bytes:
        h = sha256(PROTOCOL_NAME).digest()
        h = sha256(h + sh_public_key).digest()
        h = sha256(h + st_public_key).digest()
        h = sha256(h + eh_public_key).digest()
        h = sha256(h + bytes([sh_key_index])).digest()
        self.handshake_hash = sha256(h + et_public_key).digest()
        ck, _ = hkdf(PROTOCOL_NAME, secret_eh_et)
        ck, _ = hkdf(ck, secret_sh_et)
        ck, k_auth = hkdf(ck, secret_eh_st)
        self.k_cmd, self.k_resp = hkdf(ck, b"")
        self.nonce_cmd = 0
        self.nonce_resp = 0
        return AESGCM(k_auth).encrypt(bytes(IV_LEN), b"", self.handshake_hash)

    def is_session_valid(self) -> bool:
        return self.nonce_cmd >= 0

    def _check_nonce_sync(self) -> None:
        # Sanity check.
        # At the beginning and at the end of each encrypt/decrypt pair
        # both nonces should be synchronized.
        if self.nonce_cmd != self.nonce_resp:
            self.reset()
            raise AssertionError("Nonces out of sync.")

    def _generate_private_key(self) -> X25519PrivateKey:
        return X25519PrivateKey.from_private_bytes(
            self.random_source.urandom(X25519_KEY_LEN)
        )


class HostEncryptedSession(EncryptedSessionBase):
    """
    Implements the cryptographic operations of the secure channel that are
    specific to the host.
    """

    def reset(self) -> None:
        super().reset()
        # Host ephemeral X25519 key. Valid only during handshake.
        self.eh_private_key: Optional[X25519PrivateKey] = None

    def create_handshake_request(self) -> bytes:
        # Generate ephemeral host key pair.
        self.eh_private_key = self._generate_private_key()
        return self.eh_private_key.public_key().public_bytes_raw()

    def process_handshake_response(
        self,
        pairing_key_idx: int,
        st_public_key: bytes,
        sh_private_key: bytes,
        et_public_key: bytes,
        authentication_tag: bytes,
    ) -> None:
        if self.eh_private_key is None:
            raise RuntimeError("No handshake in progress.")

        st_public_key_obj = X25519PublicKey.from_public_bytes(st_public_key)
        sh_private_key_obj = X25519PrivateKey.from_private_bytes(sh_private_key)
        et_public_key_obj = X25519PublicKey.from_public_bytes(et_public_key)

        # Convert locally stored public keys to bytes.
        sh_public_key = sh_private_key_obj.public_key().public_bytes_raw()
        eh_public_key = self.eh_private_key.public_key().public_bytes_raw()

        # Compute shared secrets.
        secret_eh_et = self.eh_private_key.exchange(et_public_key_obj)
        secret_sh_et = sh_private_key_obj.exchange(et_public_key_obj)
        secret_eh_st = self.eh_private_key.exchange(st_public_key_obj)

        # Invalidate host's ephemeral key, since it's no longer needed.
        self.eh_private_key = None

        # Compute the session's symmetric keys.
        expected_authentication_tag = self.execute_handshake(
            pairing_key_idx,
            sh_public_key,
            st_public_key,
            eh_public_key,
            et_public_key,
            secret_eh_et,  # ephemeral-host/ephemeral-Tropic shared secret
            secret_sh_et,  # static-host/ephemeral-Tropic shared secret
            secret_eh_st,  # ephemeral-host/static-Tropic shared secret
        )

        if authentication_tag != expected_authentication_tag:
            self.reset()
            raise ValueError("Invalid handshake authentication tag.")

    def encrypt_command(self, command_plaintext: bytes) -> bytes:
        self._check_nonce_sync()
        nonce = self.nonce_cmd.to_bytes(IV_LEN, "little")
        self.nonce_cmd += 1
        command_ciphertext = encrypt(self.k_cmd, nonce, command_plaintext)
        if self.nonce_cmd > MAX_NONCE:
            self.nonce_cmd = 0
            self.k_cmd = b""

        return command_ciphertext

    def decrypt_response(self, response_ciphertext: bytes) -> Optional[bytes]:
        nonce = self.nonce_resp.to_bytes(IV_LEN, "little")
        self.nonce_resp += 1
        try:
            response_plaintext = decrypt(self.k_resp, nonce, response_ciphertext)
        except InvalidTag:
            self.reset()
            return None

        if self.nonce_resp > MAX_NONCE:
            self.reset()

        self._check_nonce_sync()
        return response_plaintext


class TropicEncryptedSession(EncryptedSessionBase):
    """
    Implements the cryptographic operations of the secure channel that are
    specific to the Tropic chip.
    """

    def process_handshake_request(
        self,
        st_private_key: bytes,
        sh_public_key: bytes,
        pairing_key_idx: int,
        eh_public_key: bytes,
    ) -> Tuple[bytes, bytes]:
        st_private_key_obj = X25519PrivateKey.from_private_bytes(st_private_key)
        sh_public_key_obj = X25519PublicKey.from_public_bytes(sh_public_key)

        # Load the host's ephemeral public key from the request data.
        eh_public_key_obj = X25519PublicKey.from_public_bytes(eh_public_key)

        # Generate Tropic's ephemeral key pair.
        et_private_key_obj = self._generate_private_key()
        et_public_key = et_private_key_obj.public_key().public_bytes_raw()

        # Convert static public keys to bytes.
        st_public_key = st_private_key_obj.public_key().public_bytes_raw()

        # Compute shared secrets.
        secret_eh_et = et_private_key_obj.exchange(eh_public_key_obj)
        secret_sh_et = et_private_key_obj.exchange(sh_public_key_obj)
        secret_eh_st = st_private_key_obj.exchange(eh_public_key_obj)

        authentication_tag = self.execute_handshake(
            pairing_key_idx,
            sh_public_key,
            st_public_key,
            eh_public_key,
            et_public_key,
            secret_eh_et,  # ephemeral-host/ephemeral-Tropic shared secret
            secret_sh_et,  # static-host/ephemeral-Tropic shared secret
            secret_eh_st,  # ephemeral-host/static-Tropic shared secret
        )

        return et_public_key, authentication_tag

    def decrypt_command(self, command_ciphertext: bytes) -> Optional[bytes]:
        self._check_nonce_sync()
        nonce = self.nonce_cmd.to_bytes(IV_LEN, "little")
        self.nonce_cmd += 1
        try:
            command_plaintext = decrypt(self.k_cmd, nonce, command_ciphertext)
        except InvalidTag:
            self.reset()
            return None

        if self.nonce_cmd > MAX_NONCE:
            self.reset()

        return command_plaintext

    def encrypt_response(self, response_plaintext: bytes) -> bytes:
        nonce = self.nonce_resp.to_bytes(IV_LEN, "little")
        self.nonce_resp += 1
        response_ciphertext = encrypt(self.k_resp, nonce, response_plaintext)
        if self.nonce_resp > MAX_NONCE:
            self.nonce_resp = 0
            self.k_resp = b""

        self._check_nonce_sync()
        return response_ciphertext
