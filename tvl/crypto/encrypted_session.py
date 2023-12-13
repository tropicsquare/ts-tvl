# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from hashlib import sha256
from hmac import HMAC
from typing import Optional, Tuple

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PROTOCOL_NAME = b"Noise_KK1_25519_AESGCM_SHA256\x00\x00\x00"

MAX_NONCE = (1 << 32) - 1
"""Maximum value of the secure channel nonce."""

IV_LEN = 12
"""Length of AES-GCM initialization vector, aka nonce."""


def hkdf(salt: bytes, input_keying_material: bytes) -> Tuple[bytes, bytes]:
    temp_key = HMAC(salt, input_keying_material, sha256).digest()
    output1 = HMAC(temp_key, b"\1", sha256).digest()
    output2 = HMAC(temp_key, output1 + b"\2", sha256).digest()
    return output1, output2


class EncryptedSessionBase:
    """
    Implements the cryptographic operations of the secure channel that are
    common to the host and the Tropic chip.
    """

    def __init__(self):
        self.reset()

    def reset(self):
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

    def _check_nonce_sync(self):
        # Sanity check.
        # At the beginning and at the end of each encrypt/decrypt pair
        # both nonces should be synchronized.
        if self.nonce_cmd != self.nonce_resp:
            self.reset()
            raise AssertionError("Nonces out of sync.")


class HostEncryptedSession(EncryptedSessionBase):
    """
    Implements the cryptographic operations of the secure channel that are
    specific to the host.
    """

    def __init__(self):
        super().__init__()
        # Host ephemeral X25519 key. Valid only during handshake.
        self.ephemeral_host_private_key: Optional[X25519PrivateKey] = None

    def create_handshake_request(self) -> bytes:
        # Generate ephemeral host key pair.
        self.ephemeral_host_private_key = X25519PrivateKey.generate()
        return self.ephemeral_host_private_key.public_key().public_bytes_raw()

    def process_handshake_response(
        self,
        pairing_key_idx: int,
        static_tropic_public_key_bytes: bytes,
        static_host_private_key_bytes: bytes,
        ephemeral_tropic_public_key_bytes: bytes,
        authentication_tag: bytes,
    ):
        if self.ephemeral_host_private_key is None:
            raise RuntimeError("No handshake in progress.")

        static_tropic_public_key = X25519PublicKey.from_public_bytes(
            static_tropic_public_key_bytes
        )
        static_host_private_key = X25519PrivateKey.from_private_bytes(
            static_host_private_key_bytes
        )
        ephemeral_tropic_public_key = X25519PublicKey.from_public_bytes(
            ephemeral_tropic_public_key_bytes
        )

        # Convert locally stored public keys to bytes.
        static_host_public_key_bytes = (
            static_host_private_key.public_key().public_bytes_raw()
        )
        ephemeral_host_public_key_bytes = (
            self.ephemeral_host_private_key.public_key().public_bytes_raw()
        )

        # Compute shared secrets.
        secret_eh_et = self.ephemeral_host_private_key.exchange(
            ephemeral_tropic_public_key
        )
        secret_sh_et = static_host_private_key.exchange(ephemeral_tropic_public_key)
        secret_eh_st = self.ephemeral_host_private_key.exchange(
            static_tropic_public_key
        )

        # Invalidate host's ephemeral key, since it's no longer needed.
        self.ephemeral_host_private_key = None

        # Compute the session's symmetric keys.
        expected_authentication_tag = self.execute_handshake(
            pairing_key_idx,
            static_host_public_key_bytes,
            static_tropic_public_key_bytes,
            ephemeral_host_public_key_bytes,
            ephemeral_tropic_public_key_bytes,
            secret_eh_et,  # ephemeral-host/ephemeral-Tropic shared secret
            secret_sh_et,  # static-host/ephemeral-Tropic shared secret
            secret_eh_st,  # ephemeral-host/static-Tropic shared secret
        )

        if authentication_tag != expected_authentication_tag:
            self.reset()
            raise ValueError("Invalid handshake authentication tag.")

    def encrypt_command(self, command_plaintext: bytes) -> bytes:
        self._check_nonce_sync()
        nonce = self.nonce_cmd.to_bytes(IV_LEN, "big")
        self.nonce_cmd += 1
        command_ciphertext = AESGCM(self.k_cmd).encrypt(nonce, command_plaintext, None)
        if self.nonce_resp > MAX_NONCE:
            self.nonce_cmd = 0
            self.k_cmd = b""

        return command_ciphertext

    def decrypt_response(self, response_ciphertext: bytes) -> Optional[bytes]:
        nonce = self.nonce_resp.to_bytes(IV_LEN, "big")
        self.nonce_resp += 1
        try:
            response_plaintext = AESGCM(self.k_resp).decrypt(
                nonce, response_ciphertext, None
            )
        except InvalidTag:
            self.reset()
            return None

        if self.nonce_cmd > MAX_NONCE:
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
        static_tropic_private_key_bytes: bytes,
        static_host_public_key_bytes: bytes,
        pairing_key_idx: int,
        ephemeral_host_public_key_bytes: bytes,
    ) -> Tuple[bytes, bytes]:
        static_tropic_private_key = X25519PrivateKey.from_private_bytes(
            static_tropic_private_key_bytes
        )
        static_host_public_key = X25519PublicKey.from_public_bytes(
            static_host_public_key_bytes
        )

        # Load the host's ephemeral public key from the request data.
        ephemeral_host_public_key = X25519PublicKey.from_public_bytes(
            ephemeral_host_public_key_bytes
        )

        # Generate Tropic's ephemeral key pair.
        ephemeral_tropic_private_key = X25519PrivateKey.generate()
        ephemeral_tropic_public_key_bytes = (
            ephemeral_tropic_private_key.public_key().public_bytes_raw()
        )

        # Convert static public keys to bytes.
        static_tropic_public_key_bytes = (
            static_tropic_private_key.public_key().public_bytes_raw()
        )

        # Compute shared secrets.
        secret_eh_et = ephemeral_tropic_private_key.exchange(ephemeral_host_public_key)
        secret_sh_et = ephemeral_tropic_private_key.exchange(static_host_public_key)
        secret_eh_st = static_tropic_private_key.exchange(ephemeral_host_public_key)

        authentication_tag = self.execute_handshake(
            pairing_key_idx,
            static_host_public_key_bytes,
            static_tropic_public_key_bytes,
            ephemeral_host_public_key_bytes,
            ephemeral_tropic_public_key_bytes,
            secret_eh_et,  # ephemeral-host/ephemeral-Tropic shared secret
            secret_sh_et,  # static-host/ephemeral-Tropic shared secret
            secret_eh_st,  # ephemeral-host/static-Tropic shared secret
        )

        return ephemeral_tropic_public_key_bytes, authentication_tag

    def decrypt_command(self, command_ciphertext: bytes) -> Optional[bytes]:
        self._check_nonce_sync()
        nonce = self.nonce_cmd.to_bytes(IV_LEN, "big")
        self.nonce_cmd += 1
        try:
            command_plaintext = AESGCM(self.k_cmd).decrypt(
                nonce, command_ciphertext, None
            )
        except InvalidTag:
            self.reset()
            return None

        if self.nonce_cmd > MAX_NONCE:
            self.reset()

        return command_plaintext

    def encrypt_response(self, response_plaintext: bytes) -> bytes:
        nonce = self.nonce_resp.to_bytes(IV_LEN, "big")
        self.nonce_resp += 1
        response_ciphertext = AESGCM(self.k_resp).encrypt(
            nonce, response_plaintext, None
        )
        if self.nonce_resp > MAX_NONCE:
            self.nonce_resp = 0
            self.k_resp = b""

        self._check_nonce_sync()
        return response_ciphertext
