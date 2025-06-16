import contextlib
from collections import defaultdict
from dataclasses import asdict, dataclass
from enum import IntEnum
from itertools import chain
from typing import (
    Any,
    ClassVar,
    DefaultDict,
    Dict,
    Mapping,
    Optional,
    Protocol,
    Tuple,
    Type,
    Union,
)

from pydantic import BaseModel
from typing_extensions import Self

from ....crypto.ecdsa import (
    ECDSA_KEY_SIZE,
    SignatureError,
    ecdsa_key_setup,
    ecdsa_sign,
    is_private_key_valid,
)
from ....crypto.eddsa import EDDSA_KEY_SIZE, eddsa_key_setup, eddsa_sign
from ....typing_utils import FixedSizeBytes
from ....utils import iter_subclasses
from .generic_partition import GenericModel

KEY_SIZE = 32


class ECCKeyError(Exception):
    pass


class ECCKeySetupError(ECCKeyError):
    pass


class ECCKeySubClassNotFoundError(ECCKeyError):
    pass


class ECCKeyExistsInSlotError(ECCKeyError):
    pass


class ECCKeyDoesNotExistInSlotError(ECCKeyError):
    pass


class CurveMismatchError(ECCKeyError):
    pass


class SignatureFailedError(ECCKeyError):
    pass


class CurveTypes(IntEnum):
    """
    Types of the curve
    Values must be the same as in the API.
    """

    P256 = 1
    """P256 Curve"""
    ED25519 = 2
    """Ed25519 Curve"""


class Origins(IntEnum):
    """
    Origin of the key: generated or stored.
    Values must be the same as in the API.
    """

    ECC_KEY_GENERATE = 1
    """Ecc Key randomly generated"""
    ECC_KEY_STORE = 2
    """Ecc Key imported from host"""


class _RandomSource(Protocol):
    def urandom(self, size: int, /, *, swap_endianness: bool = False) -> bytes:
        ...


ECCKeySubClass = Union["ECDSAKeyMemLayout", "EdDSAKeyMemLayout"]


@dataclass
class EccKey:
    CURVE: ClassVar[int]
    """Curve associated to the key"""
    a: bytes
    """Public Key"""
    origin: int
    """Origin of the key: 0x01 for generated keys, 0x02 for imported keys"""

    def __init_subclass__(cls, *, curve: int) -> None:
        cls.CURVE = curve

    def __post_init__(self) -> None:
        self.origin = Origins(self.origin).value

    @classmethod
    def find_subclass_from_curve(cls, curve: int) -> Type[ECCKeySubClass]:
        """Find a subclass with the associated type of curve."""
        for subclass in iter_subclasses(cls):
            if subclass.CURVE == curve:
                return subclass  # type: ignore
        raise ECCKeySubClassNotFoundError(f"No subclass with {curve=}.")

    def to_dict(self) -> Dict[str, Any]:
        """Dump the content of the key layout.

        Returns:
            the content of the key layout
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, __mapping: Mapping[str, Any], /) -> ECCKeySubClass:
        """Create a key layout from a configuration.

        Args:
            __mapping (Mapping[str, Any]): Content of the layout

        Raises:
            ECCKeySubClassNotFoundError: no layout can load the data.

        Returns:
            a new key layout object
        """
        for subclass in chain([cls], iter_subclasses(cls)):
            with contextlib.suppress(TypeError):
                return subclass(**__mapping)  # type: ignore
        raise ECCKeySubClassNotFoundError("No subclass matches dict layout.")

    @classmethod
    def from_key(cls, key: bytes, origin: Origins) -> Self:
        raise NotImplementedError("TODO")

    @classmethod
    def from_random_source(cls, rng: _RandomSource, origin: Origins) -> Self:
        raise NotImplementedError("TODO")


@dataclass
class ECDSAKeyMemLayout(EccKey, curve=CurveTypes.P256):
    d: bytes
    """Private Key 1"""
    w: bytes
    """Private Key 2"""

    @classmethod
    def from_key(cls, key: bytes, origin: Origins) -> Self:
        if not is_private_key_valid(key):
            raise ECCKeySetupError("Private key is out of range")
        return cls(
            d=(tup := ecdsa_key_setup(key))[0],
            w=tup[1],
            a=tup[2],
            origin=origin,
        )

    @classmethod
    def from_random_source(cls, rng: _RandomSource, origin: Origins) -> Self:
        key = rng.urandom(ECDSA_KEY_SIZE, swap_endianness=True)
        return cls(
            d=(tup := ecdsa_key_setup(key))[0],
            w=tup[1],
            a=tup[2],
            origin=origin,
        )


@dataclass
class EdDSAKeyMemLayout(EccKey, curve=CurveTypes.ED25519):
    s: bytes
    """Scalar"""
    prefix: bytes
    """Prefix"""

    @classmethod
    def from_key(cls, key: bytes, origin: Origins) -> Self:
        return cls(
            s=(tup := eddsa_key_setup(key))[0],
            prefix=tup[1],
            a=tup[2],
            origin=origin,
        )

    @classmethod
    def from_random_source(cls, rng: _RandomSource, origin: Origins) -> Self:
        return cls.from_key(rng.urandom(EDDSA_KEY_SIZE, swap_endianness=False), origin)


class EccKeys:
    def __init__(self) -> None:
        self.slots: DefaultDict[int, Optional[ECCKeySubClass]] = defaultdict(
            lambda: None
        )

    def _get_key(self, slot: int) -> EccKey:
        """Read the slot.

        Args:
            slot (int): the slot to read the slot

        Raises:
            ECCKeyDoesNotExistInSlotError: no valid key is in the slot

        Returns:
            the key contained in the slot
        """
        if (key := self.slots[slot]) is None:
            raise ECCKeyDoesNotExistInSlotError(
                "Requested slot does not contain an ECC key."
            )
        return key

    def generate(self, slot: int, curve: int, rng: _RandomSource) -> None:
        """Generate a new key from the given random source.

        Args:
            slot (int): the slot to save the key
            curve (int): the type of the curve to generate
            rng (bytes): the random source

        Raises:
            ECCKeyExistsInSlotError: a key already exists in the slot.
        """
        if self.slots[slot] is not None:
            raise ECCKeyExistsInSlotError(
                "Generate: an ECC key already exists in the requested slot."
            )
        self.slots[slot] = EccKey.find_subclass_from_curve(curve).from_random_source(
            rng, Origins.ECC_KEY_GENERATE
        )

    def store(self, slot: int, curve: int, k: bytes) -> None:
        """Generate a new key from the given private key.

        Args:
            slot (int): the slot to save the key
            curve (int): the type of the curve to generate
            k (bytes): the private key

        Raises:
            ECCKeyExistsInSlotError: a key already exists in the slot.
        """
        if self.slots[slot] is not None:
            raise ECCKeyExistsInSlotError(
                "Store: an ECC key already exists in the requested slot."
            )
        self.slots[slot] = EccKey.find_subclass_from_curve(curve).from_key(
            k, Origins.ECC_KEY_STORE
        )

    def read(self, slot: int) -> Tuple[int, bytes, int]:
        """Read the given slot.

        Args:
            slot (int): the slot to read the key

        Returns:
            the type of curve and the public key
        """
        return (key := self._get_key(slot)).CURVE, key.a, key.origin

    def erase(self, slot: int) -> None:
        """Erase the key in the slot

        Args:
            slot (int): the slot to erase the key
        """
        self.slots[slot] = None

    def to_dict(self) -> Dict[int, Any]:
        """dump a dict configuration of the Ecc object

        Returns:
            the content of the Ecc object as a dictionary
        """
        return {k: v.to_dict() for k, v in self.slots.items() if v is not None}

    @classmethod
    def from_dict(cls, __mapping: Mapping[int, Any], /) -> Self:
        """Create an Ecc object from a dict.

        Args:
            __mapping (Mapping[int, Any]): the configuration dict of the slots

        Returns:
            the Ecc object
        """
        instance = cls()
        for k, v in __mapping.items():
            instance.slots[k] = EccKey.from_dict(v)
        return instance

    def ecdsa_sign(
        self,
        slot: int,
        message_hash: bytes,
        handshake_hash: bytes,
        nonce: bytes,
    ) -> Tuple[bytes, bytes]:
        """Sign a message's hash with the ECDSA algorithm.

        Args:
            slot (int): slot where the ECDSA key is
            message_hash (bytes): the data to sign, 32 bytes
            handshake_hash (bytes): secure channel hash, 32 bytes
            nonce (bytes): secure channel nonce, 4 bytes

        Raises:
            CurveMismatchError: the key is incompatible with ECDSA signing
            SignatureFailedError: something went wrong, try again

        Returns:
            the signature (r, s)
        """
        if not isinstance(key := self._get_key(slot), ECDSAKeyMemLayout):
            raise CurveMismatchError("Key has wrong curve type for ECDSA signing.")
        try:
            return ecdsa_sign(key.d, key.w, message_hash, handshake_hash, nonce)
        except SignatureError as exc:
            raise SignatureFailedError(exc) from None

    def eddsa_sign(
        self, slot: int, message: bytes, handshake_hash: bytes, nonce: bytes
    ) -> Tuple[bytes, bytes]:
        """Sign a message with the EdDSA algorithm.

        Args:
            slot (int): slot where the EdDSA key is
            message (bytes): data to sign
            handshake_hash (bytes): secure channel handshake hash, 32 bytes
            nonce (bytes): secure channel nonce, 4 bytes

        Raises:
            CurveMismatchError: the key is incompatible with EdDSA signing

        Returns:
            the signature (r, s)
        """
        if not isinstance(key := self._get_key(slot), EdDSAKeyMemLayout):
            raise CurveMismatchError("Key has wrong curve type for EdDSA signing.")
        return eddsa_sign(key.s, key.prefix, key.a, message, handshake_hash, nonce)

    def eddsa_verify(
        self, slot: int, message_hash: bytes, r: bytes, s: bytes
    ) -> bool:
        """Verify a message hash with the EdDSA algorithm.

        Args:
            slot (int): slot where the EdDSA key is
            message_hash (bytes): the hash of the message to verify, 32 bytes
            r (bytes): the R component of the signature, 32 bytes
            s (bytes): the S component of the signature, 32 bytes

        Raises:
            CurveMismatchError: the key is incompatible with EdDSA verification

        Returns:
            True if the signature is valid, False otherwise
        """
        if not isinstance(key := self._get_key(slot), EdDSAKeyMemLayout):
            raise CurveMismatchError("Key has wrong curve type for EdDSA verification.")
        
        # Use the cryptography library's Ed25519PublicKey for verification
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
        
        try:
            public_key = Ed25519PublicKey.from_public_bytes(key.a)
            signature = r + s  # Ed25519 signature is R || S
            public_key.verify(signature, message_hash)
            return True
        except InvalidSignature:
            return False


class ECDSAKeyMemLayoutModel(BaseModel):
    d: FixedSizeBytes[KEY_SIZE]
    w: FixedSizeBytes[KEY_SIZE]
    a: FixedSizeBytes[ECDSA_KEY_SIZE]
    origin: Origins


class EdDSAKeyMemLayoutModel(BaseModel):
    s: FixedSizeBytes[KEY_SIZE]
    prefix: FixedSizeBytes[KEY_SIZE]
    a: FixedSizeBytes[EDDSA_KEY_SIZE]
    origin: Origins


class EccModel(GenericModel):
    __root__: Dict[int, Union[ECDSAKeyMemLayoutModel, EdDSAKeyMemLayoutModel]]
