# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

# GENERATED ON 2023-11-01 13:50:10.860122
# BY api_generator.py VERSION 1.4
# INPUT FILE: 3ffbc20e19bdc9da1799eff5e1ce3485c14730b894b2c56b1052599d11722657

from enum import IntEnum
from typing import List, Union

from tvl.messages.datafield import U8Array, U8Scalar, U16Scalar, params
from tvl.messages.l2_messages import L2Request, L2Response
from tvl.targets.model.base_model import BaseModel
from tvl.targets.model.meta_model import api


class L2Enum(IntEnum):
    GET_INFO_REQ = 0x01
    """Obtain information about TROPIC01"""
    HANDSHAKE_REQ = 0x02
    """Start new Secure Channel Handshake"""
    ENCRYPTED_CMD_REQ = 0x04
    """Execute L3 Command."""
    ENCRYPTED_CMD_ABT = 0x08
    """Abort execution of L3 Command."""
    RESEND_REQ = 0x10
    """Resend last Response."""
    SLEEP_REQ = 0x20
    """Move to Sleep"""
    STARTUP_REQ = 0xB3
    """Reset the chip."""
    MUTABLE_FW_UPDATE_REQ = 0xB1
    """Write new FW."""
    MUTABLE_FW_ERASE_REQ = 0xB2
    """Erase FW."""


class TsL2GetInfoReqRequest(L2Request, id=L2Enum.GET_INFO_REQ):
    object_id: U8Scalar
    """The Identifier of the requested object."""
    class ObjectIdEnum(IntEnum):
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
        """Read FW header from selected bank id (as index). Supported only in
        Start-up mode."""
    block_index: U8Scalar
    """The index of the 128 Byte long block to request"""
    class BlockIndexEnum(IntEnum):
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


class TsL2GetInfoReqResponse(L2Response, id=L2Enum.GET_INFO_REQ):
    object: U8Array[params(min_size=1, max_size=128)]
    """The data content of the requested object block."""


class TsL2HandshakeReqRequest(L2Request, id=L2Enum.HANDSHAKE_REQ):
    e_hpub: U8Array[params(size=32)]  # Ephemeral Key of Host MCU.
    """The Host MCU's Ephemeral X25519 public key. A little endian encoding of
    the x-coordinate from the public Curve25519 point."""
    pkey_index: U8Scalar  # Pairing Key Slot
    """The index of the Pairing Key slot to establish a Secure Channel Session
    with (TROPIC01 fetches $S_{HiPub}$ from the Pairing Key slot specified in
    this field)."""


class TsL2HandshakeReqResponse(L2Response, id=L2Enum.HANDSHAKE_REQ):
    e_tpub: U8Array[params(size=32)]  # Ephemeral Key of TROPIC01.
    """TROPIC01's X25519 Ephemeral key."""
    t_tauth: U8Array[params(size=16)]  # Authentication Tag
    """The Secure Channel Handshake Authentication Tag."""


class TsL2EncryptedCmdReqRequest(L2Request, id=L2Enum.ENCRYPTED_CMD_REQ):
    cmd_size: U16Scalar  # L3 Command size.
    """The size of the CMD_CIPHERTEXT L3 Field in bytes."""
    cmd_ciphertext: U8Array[params(min_size=1, max_size=4096)]  # L3 Command.
    """An encrypted L3 Command."""
    cmd_tag: U8Array[params(size=16)]  # Authentication Tag.
    """The L3 Command Authentication Tag."""


class TsL2EncryptedCmdReqResponse(L2Response, id=L2Enum.ENCRYPTED_CMD_REQ):
    res_size: U16Scalar  # L3 Result size.
    """The size of the RES_CIPHERTEXT L3 Field in bytes."""
    res_ciphertext: U8Array[params(min_size=1, max_size=4096)]  # L3 Result
    """An encrypted L3 Result."""
    res_tag: U8Array[params(size=16)]  # Authentication tag.
    """The L3 Result Authentication Tag."""


class TsL2EncryptedCmdAbtRequest(L2Request, id=L2Enum.ENCRYPTED_CMD_ABT):
    options: U8Scalar  # Command options
    class OptionsEnum(IntEnum):
        INVALIDATE_SEC_CHANNEL = 0x01
        """Bit 0 - If configured, TROPIC01 invalidates the current Secure
        Channel Session and moves to Idle Mode."""


class TsL2EncryptedCmdAbtResponse(L2Response, id=L2Enum.ENCRYPTED_CMD_ABT):
    pass


class TsL2ResendReqRequest(L2Request, id=L2Enum.RESEND_REQ):
    pass


class TsL2ResendReqResponse(L2Response, id=L2Enum.RESEND_REQ):
    pass


class TsL2SleepReqRequest(L2Request, id=L2Enum.SLEEP_REQ):
    sleep_kind: U8Scalar  # Sleep Kind
    """The type of Sleep mode TROPIC01 moves to."""
    class SleepKindEnum(IntEnum):
        SLEEP_MODE = 0x00
        """Sleep Mode"""


class TsL2SleepReqResponse(L2Response, id=L2Enum.SLEEP_REQ):
    pass


class TsL2StartupReqRequest(L2Request, id=L2Enum.STARTUP_REQ):
    startup_id: U8Scalar  # The request ID
    class StartupIdEnum(IntEnum):
        REBOOT = 0x01
        """Restart the chip and initialize it as if power-cycle was
        applied."""
        MAINTENANCE_REBOOT = 0x03
        """Restart the chip, and initialize it. Stay in "Start-up" Mode, do
        not load Mutable FW from R-Memory."""


class TsL2StartupReqResponse(L2Response, id=L2Enum.STARTUP_REQ):
    pass


class TsL2MutableFwUpdateReqRequest(L2Request, id=L2Enum.MUTABLE_FW_UPDATE_REQ):
    bank_id: U8Scalar  # The Identifier of the bank to write
    class BankIdEnum(IntEnum):
        FW1 = 0x01
        """Firmware bank 1."""
        FW2 = 0x02
        """Firmware bank 2"""
        SPECT1 = 0x11
        """SPECT bank 1."""
        SPECT2 = 0x12
        """SPECT bank 2"""
    offset: U16Scalar  # Offset for specific bank for chunk write
    data: U8Array[params(min_size=1, max_size=128)]  # Binary data to write


class TsL2MutableFwUpdateReqResponse(L2Response, id=L2Enum.MUTABLE_FW_UPDATE_REQ):
    pass


class TsL2MutableFwEraseReqRequest(L2Request, id=L2Enum.MUTABLE_FW_ERASE_REQ):
    bank_id: U8Scalar  # The Identifier of the bank to erase. The same choices as above.
    class BankIdEnum(IntEnum):
        FW1 = 0x01
        """Firmware bank 1."""
        FW2 = 0x02
        """Firmware bank 2"""
        SPECT1 = 0x11
        """SPECT bank 1."""
        SPECT2 = 0x12
        """SPECT bank 2"""


class TsL2MutableFwEraseReqResponse(L2Response, id=L2Enum.MUTABLE_FW_ERASE_REQ):
    pass


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
    def ts_l2_get_info_req(self, request: TsL2GetInfoReqRequest) -> Union[TsL2GetInfoReqResponse, List[TsL2GetInfoReqResponse]]:
        """Request to obtain information about TROPIC01. The type of
		information obtained is distinguished by OBJECT_ID. NOTE: In case the
		"Start-up" mode is active the Immutable FW is running and then any
		version identification has highest bit set to '1'. SPECT_FW_VERSION in
		that case will return dummy value of 0x80000000 because the SPECT FW
		is part of this Immutable FW."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_handshake_req(self, request: TsL2HandshakeReqRequest) -> Union[TsL2HandshakeReqResponse, List[TsL2HandshakeReqResponse]]:
        """Request to execute a Secure Channel Handshake and establish a new
		Secure Channel Session (TROPIC01 moves to Secure Channel Mode)."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_encrypted_cmd_req(self, request: TsL2EncryptedCmdReqRequest) -> Union[TsL2EncryptedCmdReqResponse, List[TsL2EncryptedCmdReqResponse]]:
        """Request to execute an L3 Command."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_encrypted_cmd_abt(self, request: TsL2EncryptedCmdAbtRequest) -> Union[TsL2EncryptedCmdAbtResponse, List[TsL2EncryptedCmdAbtResponse]]:
        """Request to abort the execution of the L3 Command and optionally
		invalidate the current Secure Channel Session (TROPIC01 moves to Idle
		Mode)."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_resend_req(self, request: TsL2ResendReqRequest) -> Union[TsL2ResendReqResponse, List[TsL2ResendReqResponse]]:
        """Request for TROPIC01 to resend the last L2 Response."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_sleep_req(self, request: TsL2SleepReqRequest) -> Union[TsL2SleepReqResponse, List[TsL2SleepReqResponse]]:
        """Request for TROPIC01 to go to Sleep Mode or Deep Sleep Mode."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_startup_req(self, request: TsL2StartupReqRequest) -> Union[TsL2StartupReqResponse, List[TsL2StartupReqResponse]]:
        """Reset the chip."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_mutable_fw_update_req(self, request: TsL2MutableFwUpdateReqRequest) -> Union[TsL2MutableFwUpdateReqResponse, List[TsL2MutableFwUpdateReqResponse]]:
        """Write chunk of new mutable FW to a R-Memory bank. Pay attention to
		write only to correctly erased bank (see Mutable_FW_Erase_Req).
		Command supported only in "Start-up" mode, i.e. after Startup_Req with
		MAINTENANCE_REBOOT."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_mutable_fw_erase_req(self, request: TsL2MutableFwEraseReqRequest) -> Union[TsL2MutableFwEraseReqResponse, List[TsL2MutableFwEraseReqResponse]]:
        """Erase mutble FW stored in a R-Memory bank. Command supported only
		in "Start-up" mode, i.e. after Startup_Req with MAINTENANCE_REBOOT."""
        raise NotImplementedError("TODO")
