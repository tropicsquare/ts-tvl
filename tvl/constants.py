# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from enum import IntFlag

from .typing_utils import HexReprIntEnum


class L1ChipStatusFlag(IntFlag):
    READY = 1
    """TROPIC01 is ready to receive L2 Request frame or L3 Command packet"""
    ALARM = 2
    """TROPIC01 is in Alarm mode"""
    START = 4
    """TROPIC01 is in Start-up mode"""


class L2IdFieldEnum(HexReprIntEnum):
    GET_RESP = 0xAA
    """Request to read L2 Response frame"""


class L2StatusEnum(HexReprIntEnum):
    """Valid STATUS field values"""

    REQ_OK = 0x01
    """TROPIC01 has received, checked for CRC validity,
    and processed the L2 Request frame."""
    RES_OK = 0x02
    """TROPIC01 has processed the L3 Command packet."""
    REQ_CONT = 0x03
    """Similar to REQ_OK"""
    RES_CONT = 0x04
    """Similar to REQ_CONT when splitted result is transmitted
    from TROPIC01 to the Host MCU."""
    RESP_DISABLED = 0x78
    """The L2 Request frame is disabled and cannot be executed."""
    HSK_ERR = 0x79
    """Secure Channel Handshake failed, and Secure Channel
    Session is not established"""
    NO_SESSION = 0x7A
    """TROPIC01 is not in Secure Channel Mode, and Host MCU has sent
    Encrypted_Cmd_Req (L2 Request frame)."""
    TAG_ERR = 0x7B
    """Invalid L3 Command packet Authentication Tag."""
    CRC_ERR = 0x7C
    """Incorrect CRC-16 checksum."""
    UNKNOWN_REQ = 0x7E
    """Unknown L2 Request frame type (REQ_ID) received."""
    GEN_ERR = 0x7F
    """Generic error (cannot be classified under other status codes)"""
    NO_RESP = 0xFF
    """No L2 Response frame available."""


class L3ResultFieldEnum(HexReprIntEnum):
    OK = 0xC3
    """Command successfully executed."""
    FAIL = 0x3C
    """Generic error"""
    UNAUTHORIZED = 0x01
    """Insufficient User Access Privileges"""
    INVALID_CMD = 0x02
    """Unknown L3 Command packet (Invalid CMD_ID)"""


CERTIFICATE_SIZE = 512
"""Length of a X509 certificate"""
CERTIFICATE_BLOCK_SIZE = 128
"""Length of a transmitted certificate block"""

S_HI_PUB_NB_SLOTS = 4
"""Number of slots for X25519 Host Public Keys"""

DH_LEN = 32
"""Length of a X25519 Diffie-Hellman public key"""

PADDING_BYTE = b"\x00"
"""L1 level padding byte value"""

ENCRYPTION_TAG_LEN = 16
"""Length of the tag added to the encrypted data after AESGCM encryption"""

CHIP_ID_SIZE = 128
"""Length of the Chip ID"""

RISCV_FW_VERSION_SIZE = 4
"""Length of the RISCV fw version"""

SPECT_FW_VERSION_SIZE = 4
"""Length of the SPECT ROM ID"""

CHUNK_SIZE = 128
"""Size of chunks sent by the model"""

MAX_L2_FRAME_DATA_LEN = 252
"""Maximum size of the DATA field of a L2 request or response"""

ENCRYPTED_PACKET_MAX_SIZE = 2 + 4096 + 16
"""Maximum size of a L3 packet after encryption"""
