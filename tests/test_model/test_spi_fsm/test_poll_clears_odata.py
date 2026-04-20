"""Test that a short GET_RESP poll (1-byte) followed by CSN high does not
leave stale data in the SpiFsm output buffer, which would prevent the next
L2 request from being processed.

This reproduces the bug documented in tassic-system-verification's
``target_drivers_utils.send_request`` where ``TsL2ResendRequest`` had to
skip the READY-bit poll to work around a model defect.

See: tassic-system-verification/tests_python/utilities/target_drivers_utils.py#L115
"""

import os
from typing import Any, Dict

import pytest

from tvl.api.l2_api import TsL2GetInfoRequest, TsL2GetInfoResponse, TsL2ResendRequest
from tvl.constants import L1ChipStatusFlag, L2IdFieldEnum, L2StatusEnum, MIN_L2_FRAME_LEN
from tvl.host.host import Host
from tvl.messages.randomize import randomize
from tvl.targets.model.tropic01_model import Tropic01Model

_CHIP_ID = os.urandom(128)


@pytest.fixture()
def model_configuration(model_configuration: Dict[str, Any]):
    model_configuration.update(
        {
            "chip_id": _CHIP_ID,
            "busy_iter": [False],  # never busy
        }
    )
    yield model_configuration


def _poll_ready_1byte(model: Tropic01Model) -> L1ChipStatusFlag:
    """Emulate a 1-byte READY poll as done by tassic-system-verification's
    ``poll_for_ready`` / ``get_chip_status_target``: send a single GET_RESP
    byte, read just the CHIP_STATUS, then end the transaction."""
    model.spi_drive_csn_low()
    response = model.spi_send(bytes([L2IdFieldEnum.GET_RESP]))
    model.spi_drive_csn_high()
    return L1ChipStatusFlag(response[0])


def _ll_send_request(model: Tropic01Model, data: bytes) -> None:
    """Send raw L2 request bytes at SPI level (no response fetch)."""
    model.spi_drive_csn_low()
    model.spi_send(data)
    model.spi_drive_csn_high()


def _ll_get_response(model: Tropic01Model) -> bytes:
    """Do a full GET_RESP transaction to fetch the response."""
    model.spi_drive_csn_low()
    recvd = model.spi_send(bytes([L2IdFieldEnum.GET_RESP]) + bytes(MIN_L2_FRAME_LEN))
    model.spi_drive_csn_high()
    return recvd


def test_poll_with_pending_response_then_new_request(model: Tropic01Model):
    """A 1-byte poll while a response is buffered, followed by a new L2
    request, must not raise RuntimeError('Response buffer not empty.')."""

    # 1. Send a request — response gets buffered
    req = randomize(
        TsL2GetInfoRequest, object_id=TsL2GetInfoRequest.ObjectIdEnum.CHIP_ID
    )
    _ll_send_request(model, req.to_bytes())

    # 2. 1-byte poll — loads odata, CSN high leaves it stale
    chip_status = _poll_ready_1byte(model)
    assert chip_status & L1ChipStatusFlag.READY

    # 3. Fetch the response properly (drain odata)
    recvd = _ll_get_response(model)
    assert recvd[1] != L2StatusEnum.NO_RESP

    # 4. Another 1-byte poll — buffer should now be empty
    chip_status = _poll_ready_1byte(model)

    # 5. Send a new request ��� must not crash with "Response buffer not empty."
    req2 = randomize(
        TsL2GetInfoRequest, object_id=TsL2GetInfoRequest.ObjectIdEnum.CHIP_ID
    )
    _ll_send_request(model, req2.to_bytes())


def test_poll_consumes_partial_odata_then_request(model: Tropic01Model):
    """The critical scenario: a 1-byte poll partially consumes the response
    (loads odata from response_buffer), CSN goes high without draining it,
    then a non-GET_RESP request arrives and hits the odata guard."""

    # 1. Send a request — response gets buffered
    req = randomize(
        TsL2GetInfoRequest, object_id=TsL2GetInfoRequest.ObjectIdEnum.CHIP_ID
    )
    _ll_send_request(model, req.to_bytes())

    # 2. 1-byte poll — odata gets loaded from response_buffer but not drained
    chip_status = _poll_ready_1byte(model)
    assert chip_status & L1ChipStatusFlag.READY

    # 3. Send a new L2 request directly — this is the operation that crashes
    #    the model with RuntimeError("Response buffer not empty.") because
    #    odata was not cleared on CSN high.
    req2 = TsL2ResendRequest()
    _ll_send_request(model, req2.to_bytes())


def test_poll_does_not_corrupt_latest_response(model: Tropic01Model, host: Host):
    """After delivering response A, if a 1-byte poll loads queued response B
    into odata and CSN goes high, a subsequent TsL2ResendRequest must still
    return A (the last *fully delivered* response), not B.

    This mirrors the tassic-system-verification test_app_grp01_035 L3 flow
    where an L2 chunk response (REQ_OK) is followed by a queued L3 result."""

    # 1. Send a GetInfo(CHIP_ID) request and fetch its response via Host
    get_info_req = randomize(
        TsL2GetInfoRequest, object_id=TsL2GetInfoRequest.ObjectIdEnum.CHIP_ID
    )
    get_info_resp = host.send_request(get_info_req)
    assert isinstance(get_info_resp, TsL2GetInfoResponse)
    assert get_info_resp.status.value == L2StatusEnum.REQ_OK
    delivered_bytes = get_info_resp.to_bytes()

    # 2. Send a *different* request at SPI level so its response is queued
    #    but NOT yet fetched.  Use RISCV_FW_VERSION to produce a response
    #    with different payload than the CHIP_ID response above.
    req2 = randomize(
        TsL2GetInfoRequest, object_id=TsL2GetInfoRequest.ObjectIdEnum.RISCV_FW_VERSION
    )
    _ll_send_request(model, req2.to_bytes())

    # 3. 1-byte poll — loads the second response into odata (calling
    #    response_buffer.next() which would overwrite latest_response).
    chip_status = _poll_ready_1byte(model)
    assert chip_status & L1ChipStatusFlag.READY

    # 4. CSN went high — odata and latest_response should be rolled back.
    #    Now ask for resend — must return the first response (delivered in
    #    step 1), NOT the second one that was only peeked at.
    resend_resp = host.send_request(TsL2ResendRequest())
    assert resend_resp.to_bytes() == delivered_bytes


def test_poll_preserves_response_for_later_fetch(model: Tropic01Model):
    """After an aborted 1-byte poll, the response that was loaded into odata
    must still be available for a subsequent full GET_RESP fetch."""

    # 1. Send a request — response gets buffered
    req = randomize(
        TsL2GetInfoRequest, object_id=TsL2GetInfoRequest.ObjectIdEnum.CHIP_ID
    )
    _ll_send_request(model, req.to_bytes())

    # 2. 1-byte poll — loads odata, CSN high re-queues it
    chip_status = _poll_ready_1byte(model)
    assert chip_status & L1ChipStatusFlag.READY

    # 3. Full GET_RESP — the response must still be available
    recvd = _ll_get_response(model)
    chip_status_byte = recvd[0]
    status_byte = recvd[1]
    assert chip_status_byte & L1ChipStatusFlag.READY
    assert status_byte != L2StatusEnum.NO_RESP
