# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from itertools import chain, islice, repeat
from typing import List, NoReturn, cast

from ...api.additional_api import L2EncryptedCmdChunk, L2EncryptedResChunk, split_data
from ...api.l2_api import (
    L2API,
    TsL2EncryptedCmdAbtRequest,
    TsL2EncryptedCmdAbtResponse,
    TsL2EncryptedCmdReqRequest,
    TsL2EncryptedCmdReqResponse,
    TsL2GetInfoReqRequest,
    TsL2GetInfoReqResponse,
    TsL2HandshakeReqRequest,
    TsL2HandshakeReqResponse,
    TsL2MutableFwEraseReqRequest,
    TsL2MutableFwUpdateReqRequest,
    TsL2ResendReqRequest,
    TsL2SleepReqRequest,
    TsL2SleepReqResponse,
    TsL2StartupReqRequest,
    TsL2StartupReqResponse,
)
from ...constants import (
    CERTIFICATE_BLOCK_SIZE,
    CHIP_ID_SIZE,
    RISCV_FW_VERSION_SIZE,
    SPECT_FW_VERSION_SIZE,
    L2StatusEnum,
)
from ...messages.l2_messages import L2Response
from ...messages.l3_messages import L3Command, L3EncryptedPacket, L3Result
from .exceptions import (
    L2ProcessingErrorContinue,
    L2ProcessingErrorGeneric,
    L2ProcessingErrorHandshake,
    L2ProcessingErrorNoSession,
    L2ProcessingErrorTag,
    L2ProcessingErrorUnknownRequest,
    L3ProcessingError,
    ResendLastResponse,
)
from .meta_model import api


class L2APIImplementation(L2API):
    def ts_l2_get_info_req(
        self, request: TsL2GetInfoReqRequest
    ) -> TsL2GetInfoReqResponse:
        object_id = request.object_id.value
        try:
            object_id = TsL2GetInfoReqRequest.ObjectIdEnum(object_id)
        except ValueError:
            raise L2ProcessingErrorGeneric(f"Invalid {object_id = }") from None
        self.logger.debug(f"{object_id = }")

        if object_id is TsL2GetInfoReqRequest.ObjectIdEnum.X509_CERTIFICATE:
            block_index = request.block_index.value
            try:
                block_index = TsL2GetInfoReqRequest.BlockIndexEnum(block_index)
            except ValueError:
                raise L2ProcessingErrorGeneric(f"Invalid {block_index = }") from None
            self.logger.debug(f"{block_index = }")
            slice_ = slice(
                block_index * CERTIFICATE_BLOCK_SIZE,
                (block_index + 1) * CERTIFICATE_BLOCK_SIZE,
            )
            object_, len_ = self.x509_certificate[slice_], CERTIFICATE_BLOCK_SIZE
        elif object_id is TsL2GetInfoReqRequest.ObjectIdEnum.CHIP_ID:
            object_, len_ = self.chip_id, CHIP_ID_SIZE
        elif object_id is TsL2GetInfoReqRequest.ObjectIdEnum.RISCV_FW_VERSION:
            object_, len_ = self.riscv_fw_version, RISCV_FW_VERSION_SIZE
        elif object_id is TsL2GetInfoReqRequest.ObjectIdEnum.SPECT_FW_VERSION:
            object_, len_ = self.spect_fw_version, SPECT_FW_VERSION_SIZE
        elif object_id is TsL2GetInfoReqRequest.ObjectIdEnum.FW_BANK:
            # Start-up mode is not modelled
            raise L2ProcessingErrorGeneric(
                f"{object_id} supported only in start-up mode."
            )
        else:
            raise NotImplementedError(f"Unsupported object id {object_id}")
        return TsL2GetInfoReqResponse(
            status=L2StatusEnum.REQ_OK,
            object=bytes(islice(chain(object_, repeat(0x00)), len_)),
        )

    def ts_l2_handshake_req(
        self, request: TsL2HandshakeReqRequest
    ) -> TsL2HandshakeReqResponse:
        s_h_pubkey = self.i_pairing_keys[(idx := request.pkey_index.value)]

        if s_h_pubkey.is_blank():
            raise L2ProcessingErrorHandshake(f"Pairing key slot #{idx} is blank.")
        if s_h_pubkey.is_invalidated():
            raise L2ProcessingErrorHandshake(f"Pairing key slot #{idx} is invalidated.")

        if self.s_t_priv is None:
            raise RuntimeError("Tropic is not paired yet.")

        e_tpub, t_tauth = self.session.process_handshake_request(
            self.s_t_priv,
            s_h_pubkey.read(),
            idx,
            request.e_hpub.to_bytes(),
        )
        self.pairing_key_slot = idx

        return TsL2HandshakeReqResponse(
            status=L2StatusEnum.REQ_OK, e_tpub=e_tpub, t_tauth=t_tauth
        )

    # TsL2EncryptedCmdReqRequest and L2EncryptedCmdChunk are compatible
    @api("l2_api", (TsL2EncryptedCmdReqRequest, L2EncryptedCmdChunk))
    def ts_l2_encrypted_cmd_req(
        self, request: TsL2EncryptedCmdReqRequest
    ) -> List[TsL2EncryptedCmdReqResponse]:
        if self.activate_encryption and not self.session.is_session_valid():
            raise L2ProcessingErrorNoSession("No valid session")

        data_field_bytes = request.data_field_bytes

        self.logger.info("Receiving L3 command.")
        if self.command_buffer.is_empty():
            total_command_length = (
                L3EncryptedPacket.MIN_NB_BYTES
                + L3EncryptedPacket.from_bytes(data_field_bytes).size.value
            )
            self.logger.debug(f"Total command length: {total_command_length}.")
            self.command_buffer.initialize(total_command_length)

        self.logger.debug(f"Add chunk {data_field_bytes}.")
        self.command_buffer.add_chunk(data_field_bytes)
        if self.command_buffer.is_command_incomplete():
            raise L2ProcessingErrorContinue("Request next L3 command chunk.")

        self.logger.info("Build encrypted packet from chunks.")
        raw_command = self.command_buffer.get_raw_command()
        self.logger.debug(raw_command)
        encrypted_command = L3EncryptedPacket.from_bytes(raw_command)
        self.logger.debug(encrypted_command)

        self.logger.info("Decrypting L3 command.")
        req_data = self._decrypt_command(encrypted_command.data_field_bytes)
        if req_data is None:
            raise L2ProcessingErrorTag("Invalid TAG in encrypted command request")
        self.logger.debug(f"Decrypted command: {req_data}")

        self.logger.info("Parsing L3 command.")
        command = L3Command.instantiate_subclass(
            L3Command.with_length(len(req_data)).from_bytes(req_data).id.value,
            req_data,
        )
        self.logger.debug(f"L3 command: {command}")

        self.logger.info("Processing L3 command.")
        try:
            result = self.process_l3_command(command)
        except L3ProcessingError as exc:
            result = L3Result(result=exc.result)
        self.logger.debug(f"L3 result: {result}")

        self.logger.info("Encrypting L3 result.")
        encrypted_result = L3EncryptedPacket.from_encrypted(
            self._encrypt_result(result.to_bytes())
        )
        self.logger.debug(f"Encrypted result: {encrypted_result}")

        self.logger.info("Creating L2 response(s).")
        chunks = [L2Response(status=L2StatusEnum.REQ_OK)]

        result_chunks = list(split_data(encrypted_result.to_bytes()))

        for i, chunk in enumerate(result_chunks, start=1):
            if i != len(result_chunks):
                status = L2StatusEnum.RES_CONT
            else:
                status = L2StatusEnum.RES_OK
            l2_chunk = L2EncryptedResChunk(status=status, encrypted_res=chunk)
            self.logger.debug(f"Chunk {i}/{len(result_chunks)}: {l2_chunk}")
            chunks.append(l2_chunk)

        # TsL2EncryptedCmdReqResponse and L2EncryptedResChunk are compatible
        return cast(List[TsL2EncryptedCmdReqResponse], chunks)

    def ts_l2_encrypted_cmd_abt(
        self, request: TsL2EncryptedCmdAbtRequest
    ) -> TsL2EncryptedCmdAbtResponse:
        request_options = request.options.value
        try:
            options = TsL2EncryptedCmdAbtRequest.OptionsEnum(request_options)
        except ValueError:
            raise L2ProcessingErrorGeneric(
                f"Unexpected value: {request_options}."
            ) from None

        self.logger.info("Aborting L3 command execution.")
        self.command_buffer.reset()

        if options is TsL2EncryptedCmdAbtRequest.OptionsEnum.INVALIDATE_SEC_CHANNEL:
            self.invalidate_session()

        self.logger.debug("L3 command execution aborted.")
        return TsL2EncryptedCmdAbtResponse(status=L2StatusEnum.REQ_OK)

    def ts_l2_resend_req(self, request: TsL2ResendReqRequest) -> NoReturn:
        if self.response_buffer.latest():
            raise ResendLastResponse("Resend the latest response.")
        raise L2ProcessingErrorGeneric("No latest response to send.")

    def ts_l2_sleep_req(self, request: TsL2SleepReqRequest) -> TsL2SleepReqResponse:
        self.check_access_privileges(
            "sleep_mode_en", self.config.cfg_sleep_mode.sleep_mode_en
        )

        request_sleep_kind = request.sleep_kind.value
        try:
            sleep_kind = TsL2SleepReqRequest.SleepKindEnum(request_sleep_kind)
        except ValueError:
            raise L2ProcessingErrorGeneric(
                f"Unexpected value: {request_sleep_kind}."
            ) from None

        self.logger.info("Entering in sleep mode.")
        if sleep_kind is TsL2SleepReqRequest.SleepKindEnum.SLEEP_MODE:
            self.invalidate_session()
            self.command_buffer.reset()
            self.response_buffer.reset()

        self.logger.debug("Entered in sleep mode.")
        return TsL2SleepReqResponse(status=L2StatusEnum.REQ_OK)

    def ts_l2_startup_req(
        self, request: TsL2StartupReqRequest
    ) -> TsL2StartupReqResponse:
        request_startup_id = request.startup_id.value
        try:
            TsL2StartupReqRequest.StartupIdEnum(request_startup_id)
        except ValueError:
            raise L2ProcessingErrorGeneric(
                f"Unexpected value: {request_startup_id}."
            ) from None

        # Start-up mode is not modelled, so only one behavior for this request
        self.logger.info("Resetting the chip.")
        self.power_off()
        self.power_on()

        self.logger.info("Chip reset.")
        return TsL2StartupReqResponse(status=L2StatusEnum.REQ_OK)

    def ts_l2_mutable_fw_update_req(
        self, request: TsL2MutableFwUpdateReqRequest
    ) -> NoReturn:
        # Start-up mode is not modelled
        raise L2ProcessingErrorUnknownRequest(
            f"{type(request)} accessible only in start-up mode."
        )

    def ts_l2_mutable_fw_erase_req(
        self, request: TsL2MutableFwEraseReqRequest
    ) -> NoReturn:
        # Start-up mode is not modelled
        raise L2ProcessingErrorUnknownRequest(
            f"{type(request)} accessible only in start-up mode."
        )
