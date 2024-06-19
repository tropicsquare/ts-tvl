# GENERATED ON 2024-06-24 09:50:34.525473
# BY internal VERSION 1.6
# INPUT FILE: 083F399F97F15AE1AE599E910C5F47186EED1E76EDE4839D2D7AFA1E149879F9
#
# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0


from tvl.messages.datafield import AUTO, U8Array, U8Scalar, U16Scalar, U32Scalar, params
from tvl.messages.l3_messages import L3Command, L3Result
from tvl.targets.model.base_model import BaseModel
from tvl.targets.model.meta_model import api
from tvl.typing_utils import HexReprIntEnum


class L3Enum(HexReprIntEnum):
    PING = 0x01
    """Ping"""
    PAIRING_KEY_WRITE = 0x10
    """Write Pairing key slot"""
    PAIRING_KEY_READ = 0x11
    """Read Pairing key slot"""
    PAIRING_KEY_INVALIDATE = 0x12
    """Invalidate Pairing Key in a slot"""
    R_CONFIG_WRITE = 0x20
    """Write R-Config"""
    R_CONFIG_READ = 0x21
    """Read R-Config"""
    R_CONFIG_ERASE = 0x22
    """Erase R-Config"""
    I_CONFIG_WRITE = 0x30
    """Write I-Config"""
    I_CONFIG_READ = 0x31
    """Read I-Config"""
    R_MEM_DATA_WRITE = 0x40
    """Write User data"""
    R_MEM_DATA_READ = 0x41
    """Read User data"""
    R_MEM_DATA_ERASE = 0x42
    """Erase User data"""
    RANDOM_VALUE_GET = 0x50
    """Get random numbers"""
    ECC_KEY_GENERATE = 0x60
    """Generate ECC Key"""
    ECC_KEY_STORE = 0x61
    """Store ECC Key"""
    ECC_KEY_READ = 0x62
    """Read Public part of ECC Key"""
    ECC_KEY_ERASE = 0x63
    """Erase ECC Key slot"""
    ECDSA_SIGN = 0x70
    """ECDSA Sign"""
    EDDSA_SIGN = 0x71
    """EDDSA Sign"""
    MCOUNTER_INIT = 0x80
    """Monotonic Counter init"""
    MCOUNTER_UPDATE = 0x81
    """Monotonic Counter update"""
    MCOUNTER_GET = 0x82
    """Read Monotonic Counter"""
    MAC_AND_DESTROY = 0x90
    """MAC-and-Destroy"""
    SERIAL_CODE_GET = 0xA0
    """Get Serial Code"""


class TsL3PingCommand(L3Command, id=L3Enum.PING):
    data_in: U8Array[params(min_size=0, max_size=4096)]  # Data in
    """The input data"""


class TsL3PingResult(L3Result, id=L3Enum.PING):
    data_out: U8Array[params(min_size=0, max_size=4096)]  # Data out
    """The output data (loopback of the DATA_IN L3 Field)."""


class TsL3PairingKeyWriteCommand(L3Command, id=L3Enum.PAIRING_KEY_WRITE):
    slot: U16Scalar  # Slot to write in
    """The Pairing Key slot. Valid values are 0 - 3."""
    class SlotEnum(HexReprIntEnum):
        PAIRING_KEY_SLOT_0 = 0x00
        """Corresponds to $S_{H0Pub}$."""
        PAIRING_KEY_SLOT_1 = 0x01
        """Corresponds to $S_{H1Pub}$."""
        PAIRING_KEY_SLOT_2 = 0x02
        """Corresponds to $S_{H2Pub}$."""
        PAIRING_KEY_SLOT_3 = 0x03
        """Corresponds to $S_{H3Pub}$."""
    padding: U8Scalar = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    s_hipub: U8Array[params(size=32)]  # Public Key
    """The X25519 public key to be written in the Pairing Key slot specified
    in the SLOT field."""


class TsL3PairingKeyWriteResult(L3Result, id=L3Enum.PAIRING_KEY_WRITE):
    pass


class TsL3PairingKeyReadCommand(L3Command, id=L3Enum.PAIRING_KEY_READ):
    slot: U16Scalar  # Slot to Read
    """The Pairing Key slot. Valid values are 0 - 3."""
    class SlotEnum(HexReprIntEnum):
        PAIRING_KEY_SLOT_0 = 0x00
        """Corresponds to $S_{H0Pub}$."""
        PAIRING_KEY_SLOT_1 = 0x01
        """Corresponds to $S_{H1Pub}$."""
        PAIRING_KEY_SLOT_2 = 0x02
        """Corresponds to $S_{H2Pub}$."""
        PAIRING_KEY_SLOT_3 = 0x03
        """Corresponds to $S_{H3Pub}$."""


class TsL3PairingKeyReadResult(L3Result, id=L3Enum.PAIRING_KEY_READ):
    class ResultEnum(HexReprIntEnum):
        PAIRING_KEY_EMPTY = 0x15
        """The Pairing key slot is in "Blank" state. A Pairing Key has not
            been written to it yet."""
        PAIRING_KEY_INVALID = 0x16
        """The Pairing key slot is in "Invalidated" state. The Pairing key
            has been invalidated."""
    padding: U8Array[params(size=3)] = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    s_hipub: U8Array[params(size=32)]  # Public Key
    """The X25519 public key to be written in the Pairing Key slot specified
    in the SLOT field."""


class TsL3PairingKeyInvalidateCommand(L3Command, id=L3Enum.PAIRING_KEY_INVALIDATE):
    slot: U16Scalar  # Slot to Invalidate
    """The Pairing Key slot. Valid values are 0 - 3."""
    class SlotEnum(HexReprIntEnum):
        PAIRING_KEY_SLOT_0 = 0x00
        """Corresponds to $S_{H0Pub}$."""
        PAIRING_KEY_SLOT_1 = 0x01
        """Corresponds to $S_{H1Pub}$."""
        PAIRING_KEY_SLOT_2 = 0x02
        """Corresponds to $S_{H2Pub}$."""
        PAIRING_KEY_SLOT_3 = 0x03
        """Corresponds to $S_{H3Pub}$."""


class TsL3PairingKeyInvalidateResult(L3Result, id=L3Enum.PAIRING_KEY_INVALIDATE):
    pass


class TsL3RConfigWriteCommand(L3Command, id=L3Enum.R_CONFIG_WRITE):
    address: U16Scalar  # Configuration object address
    """The CO address offset for TROPIC01 to compute the actual CO address."""
    padding: U8Scalar = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    value: U32Scalar  # Configuration object value
    """The CO value to write in the computed address."""


class TsL3RConfigWriteResult(L3Result, id=L3Enum.R_CONFIG_WRITE):
    pass


class TsL3RConfigReadCommand(L3Command, id=L3Enum.R_CONFIG_READ):
    address: U16Scalar  # Configuration object address
    """The CO address offset for TROPIC01 to compute the actual CO address."""


class TsL3RConfigReadResult(L3Result, id=L3Enum.R_CONFIG_READ):
    padding: U8Array[params(size=3)] = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    value: U32Scalar  # Configuration object value
    """The CO value TROPIC01 read from the computed address."""


class TsL3RConfigEraseCommand(L3Command, id=L3Enum.R_CONFIG_ERASE):
    pass


class TsL3RConfigEraseResult(L3Result, id=L3Enum.R_CONFIG_ERASE):
    pass


class TsL3IConfigWriteCommand(L3Command, id=L3Enum.I_CONFIG_WRITE):
    address: U16Scalar  # Configuration object address
    """The CO address offset for TROPIC01 to compute the actual CO address."""
    bit_index: U8Scalar  # Bit to write.
    """The bit to write from 1 to 0. Valid values are 0-31."""


class TsL3IConfigWriteResult(L3Result, id=L3Enum.I_CONFIG_WRITE):
    pass


class TsL3IConfigReadCommand(L3Command, id=L3Enum.I_CONFIG_READ):
    address: U16Scalar  # Configuration object address
    """The CO address offset for TROPIC01 to compute the actual CO address."""


class TsL3IConfigReadResult(L3Result, id=L3Enum.I_CONFIG_READ):
    padding: U8Array[params(size=3)] = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    value: U32Scalar  # Configuration object value
    """The CO value TROPIC01 read from the computed address."""


class TsL3RMemDataWriteCommand(L3Command, id=L3Enum.R_MEM_DATA_WRITE):
    udata_slot: U16Scalar  # Slot to write
    """The slot of the User Data partition. Valid values are 0 - 511."""
    padding: U8Scalar = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    data: U8Array[params(min_size=1, max_size=444)]  # Data to write
    """The data stream to be written in the slot specified in the UDATA_SLOT
    L3 field."""


class TsL3RMemDataWriteResult(L3Result, id=L3Enum.R_MEM_DATA_WRITE):
    class ResultEnum(HexReprIntEnum):
        WRITE_FAIL = 0x10
        """The slot is already written in."""
        SLOT_EXPIRED = 0x11
        """The writing operation limit is reached for the slot."""


class TsL3RMemDataReadCommand(L3Command, id=L3Enum.R_MEM_DATA_READ):
    udata_slot: U16Scalar  # Slot to read
    """The slot of the User Data partition. Valid values are 0 - 511."""


class TsL3RMemDataReadResult(L3Result, id=L3Enum.R_MEM_DATA_READ):
    padding: U8Array[params(size=3)] = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    data: U8Array[params(min_size=0, max_size=444)]  # Data to read
    """The data stream read from the slot specified in the UDATA_SLOT L3
    field."""


class TsL3RMemDataEraseCommand(L3Command, id=L3Enum.R_MEM_DATA_ERASE):
    udata_slot: U16Scalar  # Slot to erase
    """The slot of the User Data partition. Valid values are 0 - 511."""


class TsL3RMemDataEraseResult(L3Result, id=L3Enum.R_MEM_DATA_ERASE):
    pass


class TsL3RandomValueGetCommand(L3Command, id=L3Enum.RANDOM_VALUE_GET):
    n_bytes: U8Scalar  # Number of bytes to get.
    """The number of random bytes to get."""


class TsL3RandomValueGetResult(L3Result, id=L3Enum.RANDOM_VALUE_GET):
    padding: U8Array[params(size=3)] = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    random_data: U8Array[params(min_size=0, max_size=255)]  # Random data
    """The random data from TRNG2 in the number of bytes specified in the
    N_BYTES L3 Field."""


class TsL3EccKeyGenerateCommand(L3Command, id=L3Enum.ECC_KEY_GENERATE):
    slot: U16Scalar  # ECC Key slot
    """The slot to write the generated key. Valid values are 0 - 31."""
    curve: U8Scalar  # Elliptic Curve
    """The Elliptic Curve the key is generated from."""
    class CurveEnum(HexReprIntEnum):
        P256 = 0x01
        """P256 Curve - 64-byte long public key."""
        ED25519 = 0x02
        """Ed25519 Curve - 32-byte long public key."""


class TsL3EccKeyGenerateResult(L3Result, id=L3Enum.ECC_KEY_GENERATE):
    pass


class TsL3EccKeyStoreCommand(L3Command, id=L3Enum.ECC_KEY_STORE):
    slot: U16Scalar  # ECC Key slot
    """The slot to write the K L3 Field. Valid values are 0 - 31."""
    curve: U8Scalar  # The type of Elliptic Curve the K L3 Field belongs to.
    """The Elliptic Curve the key is generated from."""
    class CurveEnum(HexReprIntEnum):
        P256 = 0x01
        """P256 Curve - 64-byte long public key."""
        ED25519 = 0x02
        """Ed25519 Curve - 32-byte long public key."""
    padding: U8Array[params(size=12)] = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    k: U8Array[params(size=32)]  # Key to store
    """The ECC Key to store. The key must be a member of the field given by
    the curve specified in the CURVE L3 Field."""


class TsL3EccKeyStoreResult(L3Result, id=L3Enum.ECC_KEY_STORE):
    pass


class TsL3EccKeyReadCommand(L3Command, id=L3Enum.ECC_KEY_READ):
    slot: U16Scalar  # ECC Key slot
    """The slot to read the public ECC Key from. Valid values are 0 - 31."""


class TsL3EccKeyReadResult(L3Result, id=L3Enum.ECC_KEY_READ):
    curve: U8Scalar  # Elliptic Curve
    """The type of Elliptic Curve public key returned."""
    class CurveEnum(HexReprIntEnum):
        P256 = 0x01
        """P256 Curve - 64-byte long public key."""
        ED25519 = 0x02
        """Ed25519 Curve - 32-byte long public key."""
    origin: U8Scalar  # Origin of the key.
    """The origin of the key."""
    class OriginEnum(HexReprIntEnum):
        ECC_KEY_GENERATE = 0x01
        """The key is from key generation on the device."""
        ECC_KEY_STORE = 0x02
        """The key is from key storage in the device."""
    padding: U8Array[params(size=13)] = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    pub_key: U8Array[params(min_size=32, max_size=64)]  # Public Key
    """The public key from the ECC Key slot as specified in the SLOT L3
    Field."""


class TsL3EccKeyEraseCommand(L3Command, id=L3Enum.ECC_KEY_ERASE):
    slot: U16Scalar  # ECC Key slot
    """The slot to erase. Valid values are 0 - 31."""


class TsL3EccKeyEraseResult(L3Result, id=L3Enum.ECC_KEY_ERASE):
    pass


class TsL3EcdsaSignCommand(L3Command, id=L3Enum.ECDSA_SIGN):
    slot: U16Scalar  # ECC Key slot
    """The slot (from the ECC Keys partition in R-Memory) to read the key for
    ECDSA signing."""
    padding: U8Array[params(size=13)] = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    msg_hash: U8Array[params(size=32)]  # Hash of the Message to sign.
    """The hash of the message to sign (max size of 32 bytes)."""


class TsL3EcdsaSignResult(L3Result, id=L3Enum.ECDSA_SIGN):
    class ResultEnum(HexReprIntEnum):
        INVALID_KEY = 0x12
        """The key in the requested slot does not exist, or is invalid."""
    padding: U8Array[params(size=15)] = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    r: U8Array[params(size=32)]  # ECDSA Signature - R part
    """ECDSA signature - The R part"""
    s: U8Array[params(size=32)]  # ECDSA Signature - S part
    """ECDSA signature - The S part"""


class TsL3EddsaSignCommand(L3Command, id=L3Enum.EDDSA_SIGN):
    slot: U16Scalar  # ECC Key slot
    """The slot (from the ECC Keys partition in R-Memory) to read the key for
    EdDSA signing."""
    padding: U8Array[params(size=13)] = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    msg: U8Array[params(min_size=1, max_size=4096)]  # Message to sign.
    """The message to sign (max size of 4096 bytes)."""


class TsL3EddsaSignResult(L3Result, id=L3Enum.EDDSA_SIGN):
    class ResultEnum(HexReprIntEnum):
        INVALID_KEY = 0x12
        """The key in the requested slot does not exist, or is invalid."""
    padding: U8Array[params(size=15)] = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    r: U8Array[params(size=32)]  # EDDSA Signature - R part
    """EdDSA signature - The R part"""
    s: U8Array[params(size=32)]  # EDDSA Signature - S part
    """EdDSA signature - The S part"""


class TsL3McounterInitCommand(L3Command, id=L3Enum.MCOUNTER_INIT):
    mcounter_index: U16Scalar  # Index of Monotonic Counter
    """The index of the Monotonic Counter to initialize. Valid values are 0 -
    15."""
    padding: U8Scalar = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    mcounter_val: U32Scalar  # Initialization value.
    """The initialization value of the Monotonic Counter."""


class TsL3McounterInitResult(L3Result, id=L3Enum.MCOUNTER_INIT):
    pass


class TsL3McounterUpdateCommand(L3Command, id=L3Enum.MCOUNTER_UPDATE):
    mcounter_index: U16Scalar  # Index of Monotonic Counter
    """The index of the Monotonic Counter to update. Valid values are 0 -
    15."""


class TsL3McounterUpdateResult(L3Result, id=L3Enum.MCOUNTER_UPDATE):
    class ResultEnum(HexReprIntEnum):
        UPDATE_ERR = 0x13
        """Failure to update the specified Monotonic Counter. The
            Monotonic Counter is already at 0."""
        COUNTER_INVALID = 0x14
        """The Monotonic Counter detects an attack and is locked. The
            counter must be reinitialized."""


class TsL3McounterGetCommand(L3Command, id=L3Enum.MCOUNTER_GET):
    mcounter_index: U16Scalar  # Index of Monotonic Counter
    """The index of the Monotonic Counter to get the value of. Valid index
    values are 0 - 15."""


class TsL3McounterGetResult(L3Result, id=L3Enum.MCOUNTER_GET):
    class ResultEnum(HexReprIntEnum):
        COUNTER_INVALID = 0x14
        """The Monotonic Counter detects an attack and is locked. The
            counter must be reinitialized."""
    padding: U8Array[params(size=3)] = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    mcounter_val: U32Scalar  # Initialization value.
    """The value of the Monotonic Counter specified by the MCOUNTER_INDEX L3
    Field."""


class TsL3MacAndDestroyCommand(L3Command, id=L3Enum.MAC_AND_DESTROY):
    slot: U16Scalar  # Mac-and-Destroy slot
    """The slot (from the MAC-and-Destroy data partition in R-Memory) to
    execute the MAC_And_Destroy sequence. Valid values are 0 - 127."""
    padding: U8Scalar = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    data_in: U8Array[params(size=32)]  # Input data
    """The data input for the MAC-and-Destroy sequence."""


class TsL3MacAndDestroyResult(L3Result, id=L3Enum.MAC_AND_DESTROY):
    padding: U8Array[params(size=3)] = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    data_out: U8Array[params(size=32)]  # Output data
    """The data output from the MAC-and-Destroy sequence."""


class TsL3SerialCodeGetCommand(L3Command, id=L3Enum.SERIAL_CODE_GET):
    pass


class TsL3SerialCodeGetResult(L3Result, id=L3Enum.SERIAL_CODE_GET):
    padding: U8Array[params(size=3)] = AUTO  # Padding  # type: ignore
    """The padding by dummy data."""
    serial_code: U8Array[params(size=32)]  # Serial code
    """The unique per-chip identifier."""


class L3API(BaseModel):
    """
    Implementation of the TASSIC functional model.

    When adding a new command processing method, decorate it with the
    function `api` as shown below. Do not forget the type hint.

    ```python
    @api("l3_api")
    def handler(self, request: <in type>) -> <out type>:
        # Processing
    ```
    """

    @api("l3_api")
    def ts_l3_ping(
        self, command: TsL3PingCommand
    ) -> TsL3PingResult:
        """A dummy command to check the Secure Channel Session
		communication."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_pairing_key_write(
        self, command: TsL3PairingKeyWriteCommand
    ) -> TsL3PairingKeyWriteResult:
        """Command to write the X25519 public key to a Pairing Key slot."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_pairing_key_read(
        self, command: TsL3PairingKeyReadCommand
    ) -> TsL3PairingKeyReadResult:
        """Command to read the X25519 public key from a Pairing Key slot."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_pairing_key_invalidate(
        self, command: TsL3PairingKeyInvalidateCommand
    ) -> TsL3PairingKeyInvalidateResult:
        """Command to invalidate the X25519 public key in a Pairing Key
		slot."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_r_config_write(
        self, command: TsL3RConfigWriteCommand
    ) -> TsL3RConfigWriteResult:
        """Command to write a single CO to R-Config."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_r_config_read(
        self, command: TsL3RConfigReadCommand
    ) -> TsL3RConfigReadResult:
        """Command to read a single CO from R-Config."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_r_config_erase(
        self, command: TsL3RConfigEraseCommand
    ) -> TsL3RConfigEraseResult:
        """Command to erase the whole R-Config (convert the bits of all CO to
		1)."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_i_config_write(
        self, command: TsL3IConfigWriteCommand
    ) -> TsL3IConfigWriteResult:
        """Command to write a single bit of CO (from I-Config) from 1 to 0."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_i_config_read(
        self, command: TsL3IConfigReadCommand
    ) -> TsL3IConfigReadResult:
        """Command to read a single CO from I-Config."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_r_mem_data_write(
        self, command: TsL3RMemDataWriteCommand
    ) -> TsL3RMemDataWriteResult:
        """Command to write general purpose data in a slot from the User Data
		partition in R-Memory."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_r_mem_data_read(
        self, command: TsL3RMemDataReadCommand
    ) -> TsL3RMemDataReadResult:
        """Command to read the general purpose data from a slot of the User
		Data partition in R-Memory."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_r_mem_data_erase(
        self, command: TsL3RMemDataEraseCommand
    ) -> TsL3RMemDataEraseResult:
        """Command to erase a slot from the User Data partition in
		R-Memory."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_random_value_get(
        self, command: TsL3RandomValueGetCommand
    ) -> TsL3RandomValueGetResult:
        """Command to get random numbers generated by TRNG2."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_ecc_key_generate(
        self, command: TsL3EccKeyGenerateCommand
    ) -> TsL3EccKeyGenerateResult:
        """Command to generate an ECC Key and store the key in a slot from the
		ECC Keys partition in R-Memory."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_ecc_key_store(
        self, command: TsL3EccKeyStoreCommand
    ) -> TsL3EccKeyStoreResult:
        """Command to store an ECC Key in a slot from the ECC Keys partition
		in R-Memory."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_ecc_key_read(
        self, command: TsL3EccKeyReadCommand
    ) -> TsL3EccKeyReadResult:
        """Command to read the public ECC Key from a slot of the ECC Keys
		partition in R-Memory."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_ecc_key_erase(
        self, command: TsL3EccKeyEraseCommand
    ) -> TsL3EccKeyEraseResult:
        """Command to erase an ECC Key from a slot in the ECC Keys partition
		in R-Memory."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_ecdsa_sign(
        self, command: TsL3EcdsaSignCommand
    ) -> TsL3EcdsaSignResult:
        """Command to sign a message hash with an ECDSA algorithm."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_eddsa_sign(
        self, command: TsL3EddsaSignCommand
    ) -> TsL3EddsaSignResult:
        """Command to sign a message with an EdDSA algorithm."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_mcounter_init(
        self, command: TsL3McounterInitCommand
    ) -> TsL3McounterInitResult:
        """Command to initialize the Monotonic Counter."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_mcounter_update(
        self, command: TsL3McounterUpdateCommand
    ) -> TsL3McounterUpdateResult:
        """Command to update the Monotonic Counter (decrement by 1)."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_mcounter_get(
        self, command: TsL3McounterGetCommand
    ) -> TsL3McounterGetResult:
        """Command to get the value of the Monotonic Counter."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_mac_and_destroy(
        self, command: TsL3MacAndDestroyCommand
    ) -> TsL3MacAndDestroyResult:
        """Command to execute the MAC-and-Destroy sequence."""
        raise NotImplementedError("TODO")

    @api("l3_api")
    def ts_l3_serial_code_get(
        self, command: TsL3SerialCodeGetCommand
    ) -> TsL3SerialCodeGetResult:
        """Command to obtain the unique per-chip identifier."""
        raise NotImplementedError("TODO")
