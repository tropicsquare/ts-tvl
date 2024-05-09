# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import logging
from functools import lru_cache, partial
from inspect import signature
from itertools import chain, repeat, takewhile
from typing import (
    Any,
    Callable,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    cast,
)

from ..api.l2_api import TsL2EncryptedCmdReqRequest, TsL2EncryptedCmdReqResponse
from ..constants import L1ChipStatusFlag, L2IdFieldEnum, L2StatusEnum
from ..messages.l2_messages import L2Frame, L2Request, L2Response
from ..messages.l3_messages import L3Command, L3Packet, L3Result
from ..protocols import TropicProtocol
from .protocols import LLSendL2RequestFn, LLSendL3CommandFn

F = TypeVar("F", bound=Callable[..., Any])

Param = Mapping[str, Any]
Params = Mapping[type, Param]
OptParam = Optional[Param]


class Info(NamedTuple):
    param: OptParam
    level: int


ReceiveFn = Callable[[TropicProtocol, logging.Logger], bytes]


class TimeoutError(Exception):
    pass


class UnexpectedError(Exception):
    pass


def _send(data: bytes, target: TropicProtocol, logger: logging.Logger) -> None:
    logger.info("++ Sending raw data ++")

    logger.info("Driving Chip Select to LOW.")
    target.spi_drive_csn_low()

    logger.info("Sending raw data")
    logger.debug(f"Raw data: {data}")
    target.spi_send(data)

    logger.info("Driving Chip Select to HIGH.")
    target.spi_drive_csn_high()


def ll_receive(
    target: TropicProtocol,
    logger: logging.Logger,
    max_polling: int = 10,
    wait: int = 0,
    retry_wait: int = 0,
    padding_len: int = 4,
) -> bytes:
    if wait > 0:
        logger.info("Waiting before polling.")
        logger.debug(f"Wait time: {wait} us.")
        target.wait(wait)

    # poll for status
    logger.info("Polling for STATUS byte.")

    for i in range(start := 1, max_polling + start):
        # wait a bit until next try except at the beginning of the loop
        if i != start and retry_wait > 0:
            logger.info("Waiting before next try.")
            logger.debug(f"Retry wait time: {retry_wait} us.")
            target.wait(retry_wait)

        logger.debug(f"- attempt no. {i}.")

        # start communication
        logger.info("Driving Chip Select to LOW.")
        target.spi_drive_csn_low()

        # send GET_RESP and a few padding bytes
        recvd = target.spi_send(
            bytes([L2IdFieldEnum.GET_RESP]) + bytes(max(1, padding_len))
        )

        # CHIP_STATUS field - one byte
        chip_status = recvd[0]
        try:
            chip_status = L1ChipStatusFlag(chip_status)
            logger.debug(f"CHIP_STATUS: {chip_status!s}.")
        except ValueError:
            logger.debug(f"Unknown CHIP_STATUS: {chip_status:#04x}.")

        # STATUS field - one byte
        status = recvd[1]
        try:
            status = L2StatusEnum(status)
            logger.debug(f"STATUS: {status!s}.")
        except ValueError:
            logger.debug(f"Unknown STATUS: {status:#04x}.")

        # if a response is ready, fetch it
        if status is not L2StatusEnum.NO_RESP:
            break

        # end communication otherwise
        logger.info("Driving Chip Select to HIGH.")
        target.spi_drive_csn_high()

    else:
        raise TimeoutError(f"Target not ready after {max_polling} attempts.")

    # start accumulating bytes
    response = recvd[1:]

    # LEN field - one byte
    rsp_len = response[1]
    logger.debug(f"RSP_LEN: {rsp_len:#04x}.")

    # fetching remaining bytes
    if rsp_len > 0:
        logger.debug(f"Fetching {rsp_len} remaining bytes.")
        response += target.spi_send(bytes(rsp_len))

    # end communication
    logger.info("Driving Chip Select to HIGH.")
    target.spi_drive_csn_high()

    logger.debug(f"Received {response}.")
    return response


def ll_send_l2_request(
    data: bytes,
    target: TropicProtocol,
    logger: logging.Logger,
    receive_fn: ReceiveFn = ll_receive,
) -> bytes:
    _send(data, target, logger)
    return receive_fn(target, logger)


def ll_send_l3_command(
    cmd_chunks: List[bytes],
    target: TropicProtocol,
    logger: logging.Logger,
    max_recvd: int = 40,
    send_chunk_fn: LLSendL2RequestFn = ll_send_l2_request,
    l3_receive_fn: ReceiveFn = ll_receive,
    receive_chunk_fn: ReceiveFn = ll_receive,
) -> List[bytes]:
    def _check_status_is_req_cont(status: int) -> None:
        if status != L2StatusEnum.REQ_CONT:
            raise UnexpectedError("REQ_CONT expected after each chunk.")

    def _check_status_is_req_ok(status: int) -> None:
        if status != L2StatusEnum.REQ_OK:
            raise UnexpectedError("REQ_OK expected after the last chunk.")

    len_cmd_chunks = len(cmd_chunks)

    logger.info("Sending command chunks.")

    for i, (cmd_chunk, check_fn) in enumerate(
        zip(
            cmd_chunks,
            chain(
                repeat(_check_status_is_req_cont, times=len_cmd_chunks - 1),
                [_check_status_is_req_ok],
            ),
        ),
        start=1,
    ):
        logger.info("+ Sending chunk +")
        logger.debug(f"Chunk {i}/{len_cmd_chunks}.")
        recvd = send_chunk_fn(cmd_chunk, target, logger)
        status = recvd[0]
        check_fn(status)

    logger.info("Receiving result chunks.")
    result_chunks: List[bytes] = []

    for i, receive_fn in enumerate(
        chain([l3_receive_fn], repeat(receive_chunk_fn, times=max_recvd)),
        start=1,
    ):
        result_chunk = receive_fn(target, logger)
        logger.debug(f"Receiving chunk {i}.")
        result_chunks.append(result_chunk)
        if result_chunk[0] != L2StatusEnum.RES_CONT:
            break
    else:
        raise UnexpectedError(f"Target returned RES_CONT max={max_recvd} times.")

    return result_chunks


def partialize(base_fn: F, fn_params: OptParam = None) -> F:
    if fn_params is None:
        return base_fn

    partial_params = {
        key: value
        for key, par in signature(base_fn).parameters.items()
        if (value := fn_params.get(key, par.default)) != par.default
    }

    if not partial_params:
        return base_fn
    return cast(F, partial(base_fn, **partial_params))


class LowLevelFunctionFactory:
    """Factory for parametrizing the low level functions"""

    def __init__(self, parameters: Optional[Params] = None) -> None:
        self.parameters = parameters

    @property
    def parameters(self) -> Optional[Params]:
        return self._parameters

    @parameters.setter
    def parameters(self, parameters: Optional[Params] = None) -> None:
        self._parameters = parameters
        self.create_ll_l2_fn.cache_clear()
        self.create_ll_l3_fn.cache_clear()

    def _get_info(self, __type: type, __limit: type) -> Info:
        if self.parameters is None:
            return Info(None, 0)

        for i, class_ in enumerate(
            takewhile(lambda type_: issubclass(type_, __limit), __type.__mro__)
        ):
            if (_params := self.parameters.get(class_)) is not None:
                return Info(_params, i)

        return Info(None, 0)

    @staticmethod
    def _extract_params(tx_info: Info, rx_info: Info) -> Tuple[OptParam, OptParam]:
        # give priority to rx over tx, as well as the lower level
        if (
            tx_info.param is not None and tx_info.level < rx_info.level
        ) or rx_info.param is None:
            return tx_info.param, tx_info.param
        return tx_info.param, rx_info.param

    def get_l2_params(self, tx_l2_type: Type[L2Request]) -> Tuple[OptParam, OptParam]:
        rx_l2_type = [
            sub
            for sub in L2Frame.SUBCLASSES[tx_l2_type.ID]
            if issubclass(sub, L2Response)
        ][0]
        return self._extract_params(
            self._get_info(tx_l2_type, L2Request),
            self._get_info(rx_l2_type, L2Response),
        )

    def get_l3_params(self, tx_l3_type: Type[L3Command]) -> Tuple[OptParam, OptParam]:
        rx_l3_type = [
            sub
            for sub in L3Packet.SUBCLASSES[tx_l3_type.ID]
            if issubclass(sub, L3Result)
        ][0]
        return self._extract_params(
            self._get_info(tx_l3_type, L3Command), self._get_info(rx_l3_type, L3Result)
        )

    @lru_cache
    def create_ll_l2_fn(self, l2_type: Type[L2Request]) -> LLSendL2RequestFn:
        tx_param, rx_param = self.get_l2_params(l2_type)
        return partialize(
            partialize(ll_send_l2_request, tx_param),
            dict(receive_fn=partialize(ll_receive, rx_param)),
        )

    @lru_cache
    def create_ll_l3_fn(self, l3_type: Type[L3Command]) -> LLSendL3CommandFn:
        tx_param, rx_param = self.get_l3_params(l3_type)
        return partialize(
            partialize(ll_send_l3_command, tx_param),
            dict(
                send_chunk_fn=self.create_ll_l2_fn(TsL2EncryptedCmdReqRequest),
                l3_receive_fn=partialize(ll_receive, rx_param),
                receive_chunk_fn=partialize(
                    ll_receive,
                    self._get_info(TsL2EncryptedCmdReqResponse, L2Response).param,
                ),
            ),
        )


class FnParam(TypedDict, total=False):
    """Helper dictionary to initialize the LowLevelFunctionFactory"""

    max_polling: int  # receive
    wait: int  # receive
    retry_wait: int  # receive
    padding_len: int  # receive
    max_recvd: int  # L3 command
