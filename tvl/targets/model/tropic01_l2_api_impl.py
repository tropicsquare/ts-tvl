from itertools import chain, islice, repeat
from typing import List, NoReturn

from ...api.l2_api import (
    L2API,
    TsL2EncryptedCmdRequest,
    TsL2EncryptedCmdResponse,
    TsL2EncryptedSessionAbtRequest,
    TsL2EncryptedSessionAbtResponse,
    TsL2GetInfoRequest,
    TsL2GetInfoResponse,
    TsL2GetLogRequest,
    TsL2GetLogResponse,
    TsL2HandshakeRequest,
    TsL2HandshakeResponse,
    TsL2ResendRequest,
    TsL2SleepRequest,
    TsL2SleepResponse,
    TsL2StartupRequest,
    TsL2StartupResponse,
)
from ...constants import (
    CERTIFICATE_BLOCK_SIZE,
    CHIP_ID_SIZE,
    RISCV_FW_VERSION_SIZE,
    SPECT_FW_VERSION_SIZE,
    L2StatusEnum,
    L3ResultFieldEnum,
)
from ...messages.exceptions import NoValidSubclassError, SubclassNotFoundError
from ...messages.l2_messages import L2Response
from ...messages.l3_messages import L3Command, L3EncryptedPacket, L3Result
from .exceptions import (
    L2ProcessingErrorContinue,
    L2ProcessingErrorGeneric,
    L2ProcessingErrorHandshake,
    L2ProcessingErrorNoSession,
    L2ProcessingErrorTag,
    L3ProcessingError,
    ResendLastResponse,
)


class L2APIImplementation(L2API):
    def ts_l2_get_info(self, request: TsL2GetInfoRequest) -> TsL2GetInfoResponse:
        object_id = request.object_id.value
        try:
            object_id = TsL2GetInfoRequest.ObjectIdEnum(object_id)
        except ValueError:
            raise L2ProcessingErrorGeneric(f"Invalid {object_id = }") from None
        self.logger.debug(f"{object_id = }")

        if object_id is TsL2GetInfoRequest.ObjectIdEnum.X509_CERTIFICATE:
            block_index = request.block_index.value
            if not 0 <= block_index <= 29:
                raise L2ProcessingErrorGeneric(f"Invalid {block_index = }") from None
            self.logger.debug(f"{block_index = }")
            slice_ = slice(
                block_index * CERTIFICATE_BLOCK_SIZE,
                (block_index + 1) * CERTIFICATE_BLOCK_SIZE,
            )
            object_, len_ = self.x509_certificate[slice_], CERTIFICATE_BLOCK_SIZE
        elif object_id is TsL2GetInfoRequest.ObjectIdEnum.CHIP_ID:
            object_, len_ = self.chip_id, CHIP_ID_SIZE
        elif object_id is TsL2GetInfoRequest.ObjectIdEnum.RISCV_FW_VERSION:
            object_, len_ = self.riscv_fw_version, RISCV_FW_VERSION_SIZE
        elif object_id is TsL2GetInfoRequest.ObjectIdEnum.SPECT_FW_VERSION:
            object_, len_ = self.spect_fw_version, SPECT_FW_VERSION_SIZE
        else:
            raise NotImplementedError(f"Unsupported object id {object_id}")
        return TsL2GetInfoResponse(
            status=L2StatusEnum.REQ_OK,
            object=bytes(islice(chain(object_, repeat(0x00)), len_)),
        )

    def ts_l2_handshake(self, request: TsL2HandshakeRequest) -> TsL2HandshakeResponse:
        pkey_index = request.pkey_index.value
        try:
            pkey_index = TsL2HandshakeRequest.PkeyIndexEnum(pkey_index)
        except ValueError:
            raise L2ProcessingErrorHandshake(f"Invalid {pkey_index = }") from None
        self.logger.debug(f"{pkey_index = }")

        s_h_pubkey = self.i_pairing_keys[pkey_index]

        if not s_h_pubkey.is_valid():
            raise L2ProcessingErrorHandshake(
                f"Pairing key slot #{pkey_index} is blank or invalidated."
            )

        if self.s_t_priv is None:
            raise RuntimeError("Tropic is not paired yet.")

        e_tpub, t_tauth = self.session.process_handshake_request(
            self.s_t_priv,
            s_h_pubkey.read(),
            pkey_index,
            request.e_hpub.to_bytes(),
        )
        self.pairing_key_slot = pkey_index

        return TsL2HandshakeResponse(
            status=L2StatusEnum.REQ_OK, e_tpub=e_tpub, t_tauth=t_tauth
        )

    def ts_l2_encrypted_cmd(self, request: TsL2EncryptedCmdRequest) -> List[L2Response]:
        if self.activate_encryption and not self.session.is_session_valid():
            raise L2ProcessingErrorNoSession("No valid session")

        data_field_bytes = request.data_field_bytes

        self.logger.info("L3 command chunk received.")
        self.logger.debug(f"Raw L3 command chunk: {data_field_bytes}.")
        if self.command_buffer.is_empty():
            self.logger.debug("Received first chunk of L3 command.")
            total_command_length = (
                L3EncryptedPacket.MIN_NB_BYTES
                + L3EncryptedPacket.from_bytes(data_field_bytes).size.value
            )
            self.logger.debug(f"Total command length: {total_command_length}.")
            self.command_buffer.initialize(total_command_length)

        self.logger.debug(f"Add chunk {data_field_bytes}.")
        self.command_buffer.add_chunk(data_field_bytes)
        if self.command_buffer.is_command_incomplete():
            raise L2ProcessingErrorContinue(
                "L3 command not complete yet, requesting next chunk."
            )

        self.logger.info("All chunks received, L3 command complete.")

        raw_command = self.command_buffer.get_raw_command()
        self.logger.debug(f"Parsing raw encrypted L3 command from {raw_command}.")
        encrypted_command = L3EncryptedPacket.from_bytes(raw_command)

        self.logger.info(f"Decrypting L3 command {encrypted_command}.")
        req_data = self.decrypt_command(encrypted_command.data_field_bytes)
        if req_data is None:
            raise L2ProcessingErrorTag("Invalid TAG in encrypted command request")

        self.logger.debug(f"Parsing raw L3 command {req_data}.")
        try:
            command = self.parse_command_fn(
                L3Command.with_length(len(req_data)).from_bytes(req_data).id.value,
                req_data,
            )
        except SubclassNotFoundError as exc:
            self.logger.debug(exc)
            result = L3Result(result=L3ResultFieldEnum.INVALID_CMD)
        except NoValidSubclassError as exc:
            self.logger.debug(exc)
            result = L3Result(result=L3ResultFieldEnum.FAIL)
        else:
            self.logger.info(f"Processing L3 command {command}.")
            try:
                result = self.process_l3_command(command)
            except L3ProcessingError as exc:
                result = L3Result(result=exc.result)

        self.logger.info(f"Encrypting L3 result {result}.")
        encrypted_result = L3EncryptedPacket.from_encrypted(
            self.encrypt_result(result.to_bytes())
        )
        self.logger.debug(f"Encrypted result: {encrypted_result}")

        self.logger.info("Splitting encrypted L3 result into L2 chunk(s).")
        chunks = [L2Response(status=L2StatusEnum.REQ_OK)]

        result_chunks = list(self.split_data_fn(encrypted_result.to_bytes()))
        len_ = len(result_chunks)

        for i, (chunk, status) in enumerate(
            zip(
                result_chunks,
                chain(repeat(L2StatusEnum.RES_CONT, len_ - 1), [L2StatusEnum.RES_OK]),
            ),
            start=1,
        ):
            l2_chunk = TsL2EncryptedCmdResponse(status=status, l3_chunk=chunk)
            self.logger.debug(f"Chunk {i}/{len_}: {l2_chunk}")
            chunks.append(l2_chunk)

        return chunks

    def ts_l2_encrypted_session_abt(
        self, request: TsL2EncryptedSessionAbtRequest
    ) -> TsL2EncryptedSessionAbtResponse:
        self.invalidate_session()
        self.command_buffer.reset()

        self.logger.debug("Encrypted session aborted.")
        return TsL2EncryptedSessionAbtResponse(status=L2StatusEnum.REQ_OK)

    def ts_l2_resend(self, request: TsL2ResendRequest) -> NoReturn:
        if self.spi_fsm.response_buffer.latest():
            raise ResendLastResponse("Resend the latest response.")
        raise L2ProcessingErrorGeneric("No latest response to send.")

    def ts_l2_sleep(self, request: TsL2SleepRequest) -> TsL2SleepResponse:
        request_sleep_kind = request.sleep_kind.value
        try:
            sleep_kind = TsL2SleepRequest.SleepKindEnum(request_sleep_kind)
        except ValueError:
            raise L2ProcessingErrorGeneric(f"Invalid {request_sleep_kind = }") from None
        self.logger.debug(f"{sleep_kind = }")

        if (
            sleep_kind is TsL2SleepRequest.SleepKindEnum.SLEEP_MODE
            and self.config.cfg_sleep_mode.sleep_mode_en == 0
        ):
            self.logger.debug("Sleep mode disabled.")
            return TsL2SleepResponse(status=L2StatusEnum.RESP_DISABLED)

        self.invalidate_session()
        self.command_buffer.reset()

        self.logger.debug("Entered in sleep mode.")
        return TsL2SleepResponse(status=L2StatusEnum.REQ_OK)

    def ts_l2_startup(self, request: TsL2StartupRequest) -> TsL2StartupResponse:
        request_startup_id = request.startup_id.value
        try:
            TsL2StartupRequest.StartupIdEnum(request_startup_id)
        except ValueError:
            raise L2ProcessingErrorGeneric(
                f"Unexpected value: {request_startup_id}."
            ) from None

        # Start-up mode is not modelled, so only one behavior for this request
        self._process_power_off()

        self.logger.debug("Chip reset.")
        return TsL2StartupResponse(status=L2StatusEnum.REQ_OK)

    def ts_l2_get_log(self, request: TsL2GetLogRequest) -> TsL2GetLogResponse:
        # Return OK status to avoid issues during tests
        return TsL2GetLogResponse(status=L2StatusEnum.REQ_OK, log_msg=b"")
