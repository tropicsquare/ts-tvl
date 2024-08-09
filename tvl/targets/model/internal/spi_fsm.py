# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import logging
from itertools import cycle
from random import sample
from typing import Any, Callable, List, Optional, Sequence, Union

from ....constants import PADDING_BYTE, L1ChipStatusFlag, L2IdFieldEnum, L2StatusEnum
from ..exceptions import ResendLastResponse
from .response_buffer import ResponseBuffer

State = Callable[["SpiFsm", bytes], bytes]


def pad(data: bytes, fill: bytes, length: int) -> bytes:
    assert len(data) <= length
    assert len(fill) == 1
    return data + fill * (length - len(data))


class SpiFsm:
    def __init__(
        self,
        init_byte: bytes,
        busy_iter: Optional[Sequence[bool]],
        process_input_fn: Callable[[bytes], Union[bytes, List[bytes]]],
        logger: Optional[logging.Logger] = None,
    ) -> None:
        if logger is None:
            logger = logging.getLogger(self.__class__.__name__.lower())
        self.logger = logger

        self.init_byte = init_byte

        if busy_iter is None:
            busy_iter = sample((lst := [True] * 5 + [False] * 5), k=len(lst))
        self.busy_iter = busy_iter
        self.busy_iter_cyc = cycle(self.busy_iter)

        self.process_input_fn = process_input_fn

        self.csn_is_low = False

        self.response_buffer = ResponseBuffer()
        self.odata: bytes
        self.current_state: State
        self.reset()

    def reset(self) -> None:
        self.response_buffer.reset()
        self.odata = b""
        self.current_state = idle_state

    def spi_drive_csn_low(self) -> None:
        if not self.csn_is_low:
            self.current_state = csn_falling_edge_state
        self.csn_is_low = True

    def spi_drive_csn_high(self) -> None:
        self.current_state = idle_state
        self.csn_is_low = False

    @property
    def init_byte(self) -> bytes:
        return self._init_byte

    @init_byte.setter
    def init_byte(self, value: bytes) -> None:
        if (_l := len(value)) != 1:
            raise ValueError(f"'init_byte' should be one-byte long; got {_l}")
        self._init_byte = value

    def process_spi_data(self, rx_data: bytes) -> bytes:
        self.logger.debug(f"Received {rx_data}")
        self.logger.debug(f"State: {self.current_state.__name__}")
        tx_data = self.current_state(self, rx_data)
        self.logger.debug(f"Returning {tx_data}")
        return tx_data

    def set_next_state(self, state: State) -> None:
        self.current_state = state

    def fetch(self, length: int) -> bytes:
        """Fetch output data"""
        odata, self.odata = self.odata[:length], self.odata[length:]
        return odata


def idle_state(*_: Any) -> bytes:
    return b""


def csn_falling_edge_state(fsm: SpiFsm, data: bytes) -> bytes:
    """A transaction has just been initiated, process the received data"""

    # The first byte is GET_RESP, the chip should return a response
    if data[0] == L2IdFieldEnum.GET_RESP:
        # Sporadically set READY bit to 0 to emulate a busy chip
        if next(fsm.busy_iter_cyc):
            fsm.set_next_state(send_no_resp_state)
            return pad(
                bytes([not L1ChipStatusFlag.READY]),
                bytes([L2StatusEnum.NO_RESP]),
                len(data),
            )

        # Send data left in the output buffer
        if fsm.odata:
            fsm.set_next_state(send_response_state)
            return pad(
                bytes([L1ChipStatusFlag.READY]) + fsm.fetch((_l := len(data)) - 1),
                PADDING_BYTE,
                _l,
            )

        # Send next chunk
        if not fsm.response_buffer.is_empty():
            fsm.odata = fsm.response_buffer.next()
            fsm.set_next_state(send_response_state)
            return pad(
                bytes([L1ChipStatusFlag.READY]) + fsm.fetch((_l := len(data)) - 1),
                PADDING_BYTE,
                _l,
            )

        # Otherwise send NO_RESP
        else:
            fsm.set_next_state(send_no_resp_state)
            return pad(
                bytes([L1ChipStatusFlag.READY]),
                bytes([L2StatusEnum.NO_RESP]),
                len(data),
            )

    # The model processes only one request at a time, therefore
    # all the responses have to be fetched before sending a new request
    elif fsm.odata:
        raise RuntimeError("Response buffer not empty.")

    # Process the request that was just received
    else:
        try:
            responses_ = fsm.process_input_fn(data)
        except ResendLastResponse as exc:
            fsm.logger.info(exc)
            fsm.odata = fsm.response_buffer.latest()
            if not fsm.odata:
                raise RuntimeError("Should not happen: no latest response.")
        else:
            fsm.response_buffer.add(responses_)
            fsm.odata = fsm.response_buffer.next()

        fsm.set_next_state(send_init_byte_state)
        return pad(bytes([not L1ChipStatusFlag.READY]), fsm.init_byte, len(data))


def send_response_state(fsm: SpiFsm, data: bytes) -> bytes:
    """Send response"""
    return pad(fsm.fetch(_l := len(data)), PADDING_BYTE, _l)


def send_no_resp_state(_: Any, data: bytes) -> bytes:
    """Send NO_RESP until a new transaction is initiated"""
    return bytes([L2StatusEnum.NO_RESP]) * len(data)


def send_init_byte_state(fsm: SpiFsm, data: bytes) -> bytes:
    """Nothing in the output buffer, send init bytes"""
    return fsm.init_byte * len(data)
