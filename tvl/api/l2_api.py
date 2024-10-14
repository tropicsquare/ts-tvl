# GENERATED ON 2024-10-14 17:04:55.905797
# BY internal VERSION 1.6
# INPUT FILE: D0E700A2D97A499E9425EE2CAE6F39FAC74DE912B5F4083983367E163139880E
#
# Copyright 2024 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from typing import List, Union

from tvl.messages.datafield import U8Array, U8Scalar, U16Scalar, U32Scalar, datafield
from tvl.messages.l2_messages import L2Request, L2Response
from tvl.targets.model.base_model import BaseModel
from tvl.targets.model.meta_model import api
from tvl.typing_utils import HexReprIntEnum


class L2Enum(HexReprIntEnum):
    GET_INFO = 0x01
    """Obtain information about TROPIC01"""
    HANDSHAKE = 0x02
    """Start new Secure Channel Handshake"""
    ENCRYPTED_CMD = 0x04
    """Execute L3 Command."""
    ENCRYPTED_SESSION_ABT = 0x08
    """Abort current Secure Channel Session."""
    RESEND = 0x10
    """Resend last Response."""
    SLEEP = 0x20
    """Move to Sleep"""
    STARTUP = 0xB3
    """Reset the chip."""
    MUTABLE_FW_UPDATE = 0xB0
    """Request to enable write new FW."""
    MUTABLE_FW_UPDATE_DATA = 0xB1
    """Write new FW."""
    GET_LOG = 0xA2
    """Get FW log"""


class TsL2GetInfoRequest(L2Request, id=L2Enum.GET_INFO):
    object_id: U8Scalar
    """The Identifier of the requested object."""
    class ObjectIdEnum(HexReprIntEnum):
        X509_CERTIFICATE = 0x00
        """The X.509 chip certificate read from I-Memory and signed by Tropic
        Square (max length of 512B)."""
        CHIP_ID = 0x01
        """The chip ID - the chip silicon revision and unique device ID (max
        length of 128B)."""
        RISCV_FW_VERSION = 0x02
        """The RISCV current running FW version (4 Bytes)"""
        SPECT_FW_VERSION = 0x04
        """The SPECT FW version (4 Bytes)"""
        FW_BANK = 0xB0
        """The FW header read from the selected bank id (shown as an index).
        Supported only in Start-up mode."""
    block_index: U8Scalar
    """The index of the 128 Byte long block to request"""
    class BlockIndexEnum(HexReprIntEnum):
        DATA_CHUNK_0_127 = 0x00
        """Request for data bytes 0-127 of the object."""
        DATA_CHUNK_128_255 = 0x01
        """Request for data bytes 128-255 of the object (only needed for the
        X.509 certificate)."""
        DATA_CHUNK_256_383 = 0x02
        """Request for data bytes 128-383 of object (only needed for the X.509
        certificate)."""
        DATA_CHUNK_384_511 = 0x03
        """Request for data bytes 384-511 of object (only needed for the X.509
        certificate)."""


class TsL2GetInfoResponse(L2Response, id=L2Enum.GET_INFO):
    object: U8Array = datafield(min_size=1, max_size=128)
    """The data content of the requested object block."""


class TsL2HandshakeRequest(L2Request, id=L2Enum.HANDSHAKE):
    e_hpub: U8Array = datafield(size=32)  # Ephemeral Key of Host MCU.
    """The Host MCU's Ephemeral X25519 public key. A little endian encoding of
    the x-coordinate from the public Curve25519 point."""
    pkey_index: U8Scalar  # Pairing Key slot
    """The index of the Pairing Key slot to establish a Secure Channel Session
    with (TROPIC01 fetches $S_{HiPub}$ from the Pairing Key slot specified in
    this field)."""
    class PkeyIndexEnum(HexReprIntEnum):
        PAIRING_KEY_SLOT_0 = 0x00
        """Corresponds to $S_{H0Pub}$."""
        PAIRING_KEY_SLOT_1 = 0x01
        """Corresponds to $S_{H1Pub}$."""
        PAIRING_KEY_SLOT_2 = 0x02
        """Corresponds to $S_{H2Pub}$."""
        PAIRING_KEY_SLOT_3 = 0x03
        """Corresponds to $S_{H3Pub}$."""


class TsL2HandshakeResponse(L2Response, id=L2Enum.HANDSHAKE):
    e_tpub: U8Array = datafield(size=32)  # Ephemeral Key of TROPIC01.
    """TROPIC01's X25519 Ephemeral key."""
    t_tauth: U8Array = datafield(size=16)  # Authentication Tag
    """The Secure Channel Handshake Authentication Tag."""


class TsL2EncryptedCmdRequest(L2Request, id=L2Enum.ENCRYPTED_CMD):
    cmd_size: U16Scalar  # L3 Command size.
    """The size of the CMD_CIPHERTEXT L3 Field in bytes."""
    cmd_ciphertext: U8Array = datafield(min_size=1, max_size=4096)  # L3 Command.
    """An encrypted L3 Command."""
    cmd_tag: U8Array = datafield(size=16)  # Authentication Tag.
    """The L3 Command Authentication Tag."""


class TsL2EncryptedCmdResponse(L2Response, id=L2Enum.ENCRYPTED_CMD):
    res_size: U16Scalar  # L3 Result size.
    """The size of the RES_CIPHERTEXT L3 Field in bytes."""
    res_ciphertext: U8Array = datafield(min_size=1, max_size=4096)  # L3 Result
    """An encrypted L3 Result."""
    res_tag: U8Array = datafield(size=16)  # Authentication tag.
    """The L3 Result Authentication Tag."""


class TsL2EncryptedSessionAbtRequest(L2Request, id=L2Enum.ENCRYPTED_SESSION_ABT):
    pass


class TsL2EncryptedSessionAbtResponse(L2Response, id=L2Enum.ENCRYPTED_SESSION_ABT):
    pass


class TsL2ResendRequest(L2Request, id=L2Enum.RESEND):
    pass


class TsL2ResendResponse(L2Response, id=L2Enum.RESEND):
    pass


class TsL2SleepRequest(L2Request, id=L2Enum.SLEEP):
    sleep_kind: U8Scalar  # Sleep Kind
    """The type of Sleep mode TROPIC01 moves to."""
    class SleepKindEnum(HexReprIntEnum):
        SLEEP_MODE = 0x05
        """Sleep Mode"""
        DEEP_SLEEP_MODE = 0x0A
        """Deep Sleep Mode"""


class TsL2SleepResponse(L2Response, id=L2Enum.SLEEP):
    pass


class TsL2StartupRequest(L2Request, id=L2Enum.STARTUP):
    startup_id: U8Scalar  # The request ID
    class StartupIdEnum(HexReprIntEnum):
        REBOOT = 0x01
        """Restart, then initialize as if a power-cycle was applied."""
        MAINTENANCE_REBOOT = 0x03
        """Restart, then initialize. Stay in Start-up mode and do not load the
        mutable FW from R-Memory."""


class TsL2StartupResponse(L2Response, id=L2Enum.STARTUP):
    pass


class TsL2MutableFwUpdateRequest(L2Request, id=L2Enum.MUTABLE_FW_UPDATE):
    signature: U8Array = datafield(size=64)  # Signature of other data fields.
    """Signature of SHA256 hash of all following data in this packet."""
    hash: U8Array = datafield(size=32)  # HASH of the first FW chunk.
    """SHA256 HASH of first FW chunk of data sent using
    Mutable_FW_Update_Data."""
    type: U32Scalar  # FW type.
    """FW type which is going to be updated."""
    class TypeEnum(HexReprIntEnum):
        FW_TYPE_CPU = 0x01
        """FW for RISC-V main CPU."""
        FW_TYPE_SPECT = 0x02
        """FW for SPECT coprocessor."""
    version: U32Scalar  # Version of FW.


class TsL2MutableFwUpdateResponse(L2Response, id=L2Enum.MUTABLE_FW_UPDATE):
    pass


class TsL2MutableFwUpdateDataRequest(L2Request, id=L2Enum.MUTABLE_FW_UPDATE_DATA):
    hash: U8Array = datafield(size=32)  # HASH of the next FW chunk.
    """SHA256 HASH of the next FW chunk of data sent using
    Mutable_FW_Update_Data."""
    offset: U16Scalar  # Offset of the bank to write the FW chunk to.
    """The offset of the specific bank to write the FW chunk data to."""
    data: U8Array = datafield(min_size=4, max_size=220)  # The binary data to write.
    """The binary data to write. Data size should be a multiple of 4."""


class TsL2MutableFwUpdateDataResponse(L2Response, id=L2Enum.MUTABLE_FW_UPDATE_DATA):
    pass


class TsL2GetLogRequest(L2Request, id=L2Enum.GET_LOG):
    pass


class TsL2GetLogResponse(L2Response, id=L2Enum.GET_LOG):
    log_msg: U8Array = datafield(min_size=0, max_size=255)  # Log message
    """Log message of RISCV FW."""


class L2API(BaseModel):
    """
    Implementation of the TASSIC functional model.

    When adding a new request processing method, decorate it with the
    function `api` as shown below. Do not forget the type hint.

    ```python
    @api("l2_api")
    def handler(self, request: <in type>) -> Union[<out type>, List[<out type>]]:
        # Processing
    ```
    """

    @api("l2_api")
    def ts_l2_get_info(
        self, request: TsL2GetInfoRequest
    ) -> Union[TsL2GetInfoResponse, List[TsL2GetInfoResponse]]:
        """Request to obtain information about TROPIC01. The type of
		information obtained is distinguished by OBJECT_ID.  NOTE: If Start-up
		mode is active, TROPIC01 executes the immutable FW. Any version
		identification then has the highest bit set to 1. SPECT_FW_VERSION
		then returns a dummy value of 0x80000000 because the SPECT FW is part
		of the immutable FW."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_handshake(
        self, request: TsL2HandshakeRequest
    ) -> Union[TsL2HandshakeResponse, List[TsL2HandshakeResponse]]:
        """Request to execute a Secure Channel Handshake and establish a new
		Secure Channel Session (TROPIC01 moves to Secure Channel Mode)."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_encrypted_cmd(
        self, request: TsL2EncryptedCmdRequest
    ) -> Union[TsL2EncryptedCmdResponse, List[TsL2EncryptedCmdResponse]]:
        """Request to execute an L3 Command."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_encrypted_session_abt(
        self, request: TsL2EncryptedSessionAbtRequest
    ) -> Union[TsL2EncryptedSessionAbtResponse, List[TsL2EncryptedSessionAbtResponse]]:
        """Request to abort current Secure Channel Session and execution of L3
		command (TROPIC01 moves to Idle Mode)."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_resend(
        self, request: TsL2ResendRequest
    ) -> Union[TsL2ResendResponse, List[TsL2ResendResponse]]:
        """Request for TROPIC01 to resend the last L2 Response."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_sleep(
        self, request: TsL2SleepRequest
    ) -> Union[TsL2SleepResponse, List[TsL2SleepResponse]]:
        """Request for TROPIC01 to go to Sleep Mode or Deep Sleep Mode."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_startup(
        self, request: TsL2StartupRequest
    ) -> Union[TsL2StartupResponse, List[TsL2StartupResponse]]:
        """Request for TROPIC01 to reset."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_mutable_fw_update(
        self, request: TsL2MutableFwUpdateRequest
    ) -> Union[TsL2MutableFwUpdateResponse, List[TsL2MutableFwUpdateResponse]]:
        """Request to start updating mutable FW. Supported only in Start-up
		mode (i.e. after Startup_Req with MAINTENANCE_REBOOT). Possible update
		only same or newer version.  NOTE: Chip automatically select memory
		space for FW storage and erase it."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_mutable_fw_update_data(
        self, request: TsL2MutableFwUpdateDataRequest
    ) -> Union[TsL2MutableFwUpdateDataResponse, List[TsL2MutableFwUpdateDataResponse]]:
        """Request to write a chunk of the new mutable FW to a R-Memory bank.
		Supported only in Start-up mode after Mutable_FW_Update_Req
		successfully processed."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_get_log(
        self, request: TsL2GetLogRequest
    ) -> Union[TsL2GetLogResponse, List[TsL2GetLogResponse]]:
        """Get log from FW running on RISCV CPU."""
        raise NotImplementedError("TODO")
