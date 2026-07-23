# GENERATED ON 2026-07-23 17:45:17.084457
# BY API_GENERATOR VERSION 1.7
# INPUT FILE: 9CF2A59F9B6E0743DC728418568F484547B5FF3523B77846793EAD107CEE1B39
#

from typing import List, Union

from tvl.messages.datafield import U8Array, U8Scalar, datafield
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
    GET_LOG = 0xA2
    """Get debug log message"""


class APIL2Request(L2Request):
    """API base class for L2Request-derived classes"""


class APIL2Response(L2Response):
    """API base class for L2Response-derived classes"""


class TsL2GetInfoRequest(APIL2Request, id=L2Enum.GET_INFO):
    object_id: U8Scalar
    """The Identifier of the requested object."""
    class ObjectIdEnum(HexReprIntEnum):
        X509_CERTIFICATE = 0x00
        """The X.509 Certificate Store (object size 3840B)."""
        CHIP_ID = 0x01
        """The chip ID - the chip silicon revision and unique device ID
        (object size 128B)."""
        RISCV_FW_VERSION = 0x02
        """Current version of RISC-V FW (object size 4B)"""
        SPECT_FW_VERSION = 0x04
        """Current version of SPECT FW (object size 4B)"""
    block_index: U8Scalar  # The index of the 128B long block to request.
    """X509_CERTIFICATE: index of the 128B certificate block 0 - 29 CHIP_ID,
    *_FW_VERSION: do not care"""


class TsL2GetInfoResponse(APIL2Response, id=L2Enum.GET_INFO):
    object: U8Array = datafield(min_size=1, max_size=128)
    """The data content of the requested object block."""


class TsL2HandshakeRequest(APIL2Request, id=L2Enum.HANDSHAKE):
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


class TsL2HandshakeResponse(APIL2Response, id=L2Enum.HANDSHAKE):
    e_tpub: U8Array = datafield(size=32)  # Ephemeral Key of TROPIC01.
    """TROPIC01's X25519 Ephemeral key."""
    t_tauth: U8Array = datafield(size=16)  # Authentication Tag
    """The Secure Channel Handshake Authentication Tag."""


class TsL2EncryptedCmdRequest(APIL2Request, id=L2Enum.ENCRYPTED_CMD):
    l3_chunk: U8Array = datafield(min_size=1, max_size=252)  # L3 command.
    """The encrypted L3 command or a chunk of it."""


class TsL2EncryptedCmdResponse(APIL2Response, id=L2Enum.ENCRYPTED_CMD):
    l3_chunk: U8Array = datafield(min_size=1, max_size=252)  # L3 result.
    """The encrypted L3 result or a chunk of it."""


class TsL2EncryptedSessionAbtRequest(APIL2Request, id=L2Enum.ENCRYPTED_SESSION_ABT):
    pass


class TsL2EncryptedSessionAbtResponse(APIL2Response, id=L2Enum.ENCRYPTED_SESSION_ABT):
    pass


class TsL2ResendRequest(APIL2Request, id=L2Enum.RESEND):
    pass


class TsL2ResendResponse(APIL2Response, id=L2Enum.RESEND):
    pass


class TsL2SleepRequest(APIL2Request, id=L2Enum.SLEEP):
    sleep_kind: U8Scalar  # Sleep Kind
    """The type of Sleep mode TROPIC01 moves to."""
    class SleepKindEnum(HexReprIntEnum):
        SLEEP_MODE = 0x05
        """Sleep Mode"""


class TsL2SleepResponse(APIL2Response, id=L2Enum.SLEEP):
    pass


class TsL2StartupRequest(APIL2Request, id=L2Enum.STARTUP):
    startup_id: U8Scalar  # The request ID
    class StartupIdEnum(HexReprIntEnum):
        REBOOT = 0x01
        """Restart, then initialize as if a power-cycle was applied."""
        MAINTENANCE_REBOOT = 0x03
        """Restart, then initialize. Stay in Start-up mode and do not load the
        mutable FW from R-Memory."""


class TsL2StartupResponse(APIL2Response, id=L2Enum.STARTUP):
    pass


class TsL2GetLogRequest(APIL2Request, id=L2Enum.GET_LOG):
    pass


class TsL2GetLogResponse(APIL2Response, id=L2Enum.GET_LOG):
    log_msg: U8Array = datafield(min_size=0, max_size=252)  # Debug log message
    """Debug log message"""


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

    parse_request_fn = APIL2Request.instantiate_subclass
    """Retrieve a APIL2Request from raw data"""

    @api("l2_api")
    def ts_l2_get_info(
        self,
        request: TsL2GetInfoRequest
    ) -> Union[L2Response, List[L2Response]]:
        """Request to obtain information about TROPIC01."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_handshake(
        self,
        request: TsL2HandshakeRequest
    ) -> Union[L2Response, List[L2Response]]:
        """Request to execute a Secure Channel Handshake and establish a new
		Secure Channel Session (TROPIC01 moves to Secure Channel Mode)."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_encrypted_cmd(
        self,
        request: TsL2EncryptedCmdRequest
    ) -> Union[L2Response, List[L2Response]]:
        """Request to execute an L3 Command."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_encrypted_session_abt(
        self,
        request: TsL2EncryptedSessionAbtRequest
    ) -> Union[L2Response, List[L2Response]]:
        """Request to abort current Secure Channel Session and execution of L3
		command (TROPIC01 moves to Idle Mode)."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_resend(
        self,
        request: TsL2ResendRequest
    ) -> Union[L2Response, List[L2Response]]:
        """Request for TROPIC01 to resend the last L2 Response."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_sleep(
        self,
        request: TsL2SleepRequest
    ) -> Union[L2Response, List[L2Response]]:
        """Request for TROPIC01 to go to Sleep Mode."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_startup(
        self,
        request: TsL2StartupRequest
    ) -> Union[L2Response, List[L2Response]]:
        """Request for TROPIC01 to reset."""
        raise NotImplementedError("TODO")

    @api("l2_api")
    def ts_l2_get_log(
        self,
        request: TsL2GetLogRequest
    ) -> Union[L2Response, List[L2Response]]:
        """Get debug log message (for internal development purpose only).
		Note: Logging is irreversibly disabled in CFG_DEBUG[FW_LOG_EN] during
		provisioning."""
        raise NotImplementedError("TODO")
