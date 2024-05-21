# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import contextlib
import functools
import logging
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    overload,
)

from typing_extensions import Self

from ..api.additional_api import L2EncryptedCmdChunk, L2EncryptedResChunk, split_data
from ..api.l2_api import TsL2HandshakeReqResponse, TsL2StartupReqResponse
from ..constants import ENCRYPTION_TAG_LEN, L2StatusEnum, L3ResultFieldEnum
from ..crypto.encrypted_session import HostEncryptedSession
from ..messages.l2_messages import L2Request, L2Response
from ..messages.l3_messages import L3Command, L3EncryptedPacket, L3Result
from ..random_number_generator import RandomNumberGenerator
from .low_level_communication import LowLevelFunctionFactory
from .protocols import FunctionFactory, TargetDriver, TropicProtocol
from .simple_target_driver import SimpleTargetDriver

T = TypeVar("T")


class HostError(Exception):
    pass


class InitializationError(HostError):
    pass


class SessionError(HostError):
    pass


class NoTargetDriverError(HostError):
    pass


class NoResultError(HostError):
    pass


class Host:
    def __init__(
        self,
        *,
        target: Optional[TropicProtocol] = None,
        target_driver: Optional[TargetDriver] = None,
        s_h_priv: Optional[bytes] = None,
        s_h_pub: Optional[bytes] = None,
        s_t_pub: Optional[bytes] = None,
        pairing_key_index: Optional[int] = None,
        activate_encryption: bool = True,
        split_data_fn: Callable[[bytes], Iterator[bytes]] = split_data,
        function_factory: Optional[FunctionFactory] = None,
        debug_random_value: Optional[bytes] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        def __i(value: Optional[T], default: Any) -> T:
            if value is not None:
                return value
            if callable(default):
                return default()
            return default

        if logger is None:
            logger = logging.getLogger(self.__class__.__name__.lower())
        self.logger = logger

        if target is not None and target_driver is not None:
            raise InitializationError(
                "'target' and 'target_driver' cannot be set at the same time."
            )
        if target is not None:
            self.set_target(target)
        else:
            self._target_driver = target_driver
        """target driver addressed by the host"""
        self.s_h_priv = s_h_priv
        """Host static X25519 private key"""
        self.s_h_pub = s_h_pub
        """Host static X25519 public key"""
        self.s_t_pub = s_t_pub
        """Tropic static X25519 public key and index.
        Valid once the host and Tropic chip have been paired."""
        self.pairing_key_index = __i(pairing_key_index, -1)
        """Index at which the host public key is stored in the Tropic chip"""
        self.rng = RandomNumberGenerator(debug_random_value)
        self.session = HostEncryptedSession(random_source=self.rng)
        """Encrypted session"""
        self.activate_encryption = activate_encryption
        """Encrypt L3-layer messages"""
        self.function_factory = __i(function_factory, LowLevelFunctionFactory)
        """Create low level function adapted to the message being processed"""
        self.split_data_fn = split_data_fn
        """Used for spliting L3 commands"""

    @property
    def target_driver(self) -> TargetDriver:
        """target driver addressed by the host"""
        if self._target_driver is None:
            raise NoTargetDriverError(
                "No target driver to handle communication with target(s)."
            )
        return self._target_driver

    def __enter__(self) -> Self:
        self.target_driver.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self.target_driver.__exit__()

    def to_dict(self) -> Dict[str, Any]:
        return dict(
            s_h_priv=self.s_h_priv,
            s_h_pub=self.s_h_pub,
            s_t_pub=self.s_t_pub,
            pairing_key_index=self.pairing_key_index,
            activate_encryption=self.activate_encryption,
            debug_random_value=self.rng.debug_random_value,
        )

    @classmethod
    def from_dict(cls, __mapping: Mapping[str, Any], /) -> Self:
        def __s(n: str) -> Mapping[str, Any]:
            if (v := __mapping.get(n)) is None:
                return {}
            return {n: v}

        return cls(
            **__s("s_h_priv"),
            **__s("s_h_pub"),
            **__s("s_t_pub"),
            **__s("pairing_key_index"),
            **__s("activate_encryption"),
            **__s("debug_random_value"),
        )

    def set_logger(self, logger: logging.Logger) -> Self:
        self.logger = logger
        return self

    def set_target(self, target: TropicProtocol) -> Self:
        self._target_driver = SimpleTargetDriver(target)
        return self

    def set_target_driver(self, target_driver: TargetDriver) -> Self:
        self._target_driver = target_driver
        return self

    @overload
    def send_request(self, request: bytes) -> bytes:
        ...

    @overload
    def send_request(self, request: L2Request) -> L2Response:
        ...

    def send_request(self, request: Any) -> Any:
        return self._send_request(request)

    @functools.singledispatchmethod
    def _send_request(self, request: Any) -> Any:
        raise TypeError(f"{type(request)} not supported.")

    def _ll_send_l2(self, l2request: L2Request) -> Tuple[L2Response, bytes]:
        self.logger.debug(f"L2 request: {l2request}.")

        raw = self.target_driver.send_l2_request(
            self.function_factory.create_ll_l2_fn(type(l2request)),
            l2request.to_bytes(),
        )

        try:
            l2response = L2Response.instantiate_subclass(l2request.ID, raw)
        except Exception as exc:
            self.logger.debug(exc)
            l2response = L2Response.with_length(len(raw)).from_bytes(raw)
        self.logger.debug(f"L2 response: {l2response}.")

        status_field = l2response.status.value
        with contextlib.suppress(ValueError):
            status_field = L2StatusEnum(status_field)
        self.logger.debug(f"Status field: {status_field!r}.")

        # process response before returning it
        l2response = self._process_response(l2response)

        return l2response, raw

    @_send_request.register
    def _send_l2_request_bytes(self, request: bytes) -> bytes:
        self.logger.info("++++++ Sending raw L2 request ++++++")
        self.logger.debug(f"Raw L2 request: {request}.")
        l2req = L2Request.with_length(len(request)).from_bytes(request)
        try:
            l2req = L2Request.instantiate_subclass(l2req.id.value, request)
        except Exception as exc:
            self.logger.debug(exc)
        _, response = self._ll_send_l2(l2req)
        self.logger.debug(f"Raw L2 response: {response}.")
        self.logger.info("++++++ Returning raw L2 response ++++++")
        return response

    @_send_request.register
    def _send_l2_request(self, l2request: L2Request) -> L2Response:
        self.logger.info("++++++ Sending L2 request ++++++")
        response, _ = self._ll_send_l2(l2request)
        self.logger.info("++++++ Returning L2 response ++++++")
        return response

    @functools.singledispatchmethod
    def _process_response(self, l2response: L2Response) -> L2Response:
        return l2response

    @_process_response.register
    def _(self, l2response: TsL2HandshakeReqResponse) -> TsL2HandshakeReqResponse:
        self.logger.info(f"+ Processing {l2response} +")
        if self.s_t_pub is None:
            raise InitializationError("Host is not paired yet.")
        if self.s_h_priv is None:
            raise InitializationError("Host does not have any private key.")

        self.session.process_handshake_response(
            self.pairing_key_index,
            self.s_t_pub,
            self.s_h_priv,
            l2response.e_tpub.to_bytes(),
            l2response.t_tauth.to_bytes(),
        )
        return l2response

    @_process_response.register
    def _(self, l2response: TsL2StartupReqResponse) -> TsL2StartupReqResponse:
        self.logger.info(f"+ Processing {l2response} +")

        with contextlib.suppress(ValueError):
            status = L2StatusEnum(l2response.status.value)
            if status is L2StatusEnum.REQ_OK:
                self.session.reset()

        return l2response

    @overload
    def send_command(self, command: bytes) -> bytes:
        ...

    @overload
    def send_command(self, command: L3Command) -> L3Result:
        ...

    def send_command(self, command: Any) -> Any:
        return self._send_command(command)

    @functools.singledispatchmethod
    def _send_command(self, command: Any) -> Any:
        raise TypeError(f"{type(command)} not supported.")

    @_send_command.register
    def _ll_send_l3(self, l3command: L3Command) -> bytes:
        self.logger.debug(f"L3 command: {l3command}.")

        self.logger.info("Encrypting L3 command.")
        encrypted_command = L3EncryptedPacket.from_encrypted(
            self._encrypt_command(l3command.to_bytes())
        )
        self.logger.debug(f"Encrypted command: {encrypted_command}.")

        encrypted_chunks = list(self.split_data_fn(encrypted_command.to_bytes()))
        nb_cmd_chunks = len(encrypted_chunks)

        self.logger.info("Creating command chunks.")
        command_chunks: List[bytes] = []
        for i, chunk in enumerate(encrypted_chunks, start=1):
            self.logger.debug(f"Creating command chunk {i}/{nb_cmd_chunks}.")
            chunk = L2EncryptedCmdChunk(encrypted_cmd=chunk)
            self.logger.debug(f"Chunk: {chunk}.")
            command_chunks.append(chunk.to_bytes())

        self.logger.info("Sending command chunks.")
        raw_result_chunks = self.target_driver.send_l3_command(
            self.function_factory.create_ll_l3_fn(type(l3command)),
            command_chunks,
        )
        nb_res_chunks = len(raw_result_chunks)

        self.logger.info("Parsing result chunks.")
        result_chunks: List[bytes] = []
        for i, raw in enumerate(raw_result_chunks, start=1):
            self.logger.debug(f"Parsing result chunk {i}/{nb_res_chunks}.")
            chunk = L2EncryptedResChunk.from_bytes(raw)
            self.logger.debug(f"Chunk: {chunk}.")
            result_chunks.append(chunk.encrypted_res.to_bytes())

        self.logger.info("Assembling result chunks.")
        if not (result_bytes := b"".join(result_chunks)):
            raise NoResultError("Empty L3 result.")

        encrypted = L3EncryptedPacket.from_bytes(result_bytes)

        self.logger.info("Decrypting L3 result.")
        result = self._decrypt_result(encrypted.data_field_bytes)
        if result is None:
            raise SessionError("Invalid TAG.")
        self.logger.debug(f"Decrypted result: {result}.")
        return result

    @_send_command.register
    def _send_l3_command_bytes(self, command: bytes) -> bytes:
        self.logger.info("++++++ Sending raw L3 command ++++++")
        self.logger.debug(f"Raw L3 command: {command}.")
        l3cmd = L3Command.with_length(len(command)).from_bytes(command)
        try:
            l3cmd = L3Command.instantiate_subclass(l3cmd.id.value, command)
        except Exception as exc:
            self.logger.debug(exc)
        result = self._ll_send_l3(l3cmd)
        self.logger.debug(f"Raw L3 result: {result}.")
        self.logger.info("++++++ Returning raw L3 result ++++++")
        return result

    @_send_command.register
    def _send_l3_command(self, l3command: L3Command) -> L3Result:
        self.logger.info("++++++ Sending L3 command ++++++")
        result = self._ll_send_l3(l3command)

        self.logger.info("Parsing L3 result.")
        try:
            l3result = L3Result.instantiate_subclass(l3command.ID, result)
        except Exception as exc:
            self.logger.debug(exc)
            l3result = L3Result.with_length(len(result)).from_bytes(result)
        self.logger.debug(f"L3 result: {l3result}.")

        result_field = l3result.result.value
        with contextlib.suppress(ValueError):
            result_field = L3ResultFieldEnum(result_field)
        self.logger.debug(f"Result field: {result_field!r}.")

        self.logger.info("++++++ Returning L3 result ++++++")
        return l3result

    def _encrypt_command(self, command: bytes) -> bytes:
        if not self.activate_encryption:
            return command + b"\x00" * ENCRYPTION_TAG_LEN
        if not self.session.is_session_valid():
            raise SessionError("Cannot encrypt command: no valid session.")
        return self.session.encrypt_command(command)

    def _decrypt_result(self, result: bytes) -> Optional[bytes]:
        if not self.activate_encryption:
            return result[:-ENCRYPTION_TAG_LEN]
        if not self.session.is_session_valid():
            raise SessionError("Cannot decrypt result: no valid session.")
        return self.session.decrypt_response(result)
