from typing import Any, Dict, List, Tuple

import pytest

from tvl.api.l2_api import (
    TsL2GetInfoRequest,
    TsL2GetLogRequest,
)
from tvl.constants import L1ChipStatusFlag, L2IdFieldEnum, L2StatusEnum
from tvl.messages.l2_messages import L2Request
from tvl.targets.model.tropic01_model import Tropic01Model


REQUESTS_TO_TEST: List[Tuple[L2Request, L2StatusEnum]] = [
    (
        TsL2GetInfoRequest(
            object_id=TsL2GetInfoRequest.ObjectIdEnum.CHIP_ID, block_index=0
        ),
        L2StatusEnum.REQ_OK,
    ),
    (
        TsL2GetInfoRequest(
            object_id=TsL2GetInfoRequest.ObjectIdEnum.RISCV_FW_VERSION,
            block_index=0,
        ),
        L2StatusEnum.REQ_OK,
    ),
    (
        TsL2GetInfoRequest(
            object_id=TsL2GetInfoRequest.ObjectIdEnum.SPECT_FW_VERSION,
            block_index=0,
        ),
        L2StatusEnum.REQ_OK,
    ),
    (
        TsL2GetInfoRequest(
            object_id=TsL2GetInfoRequest.ObjectIdEnum.X509_CERTIFICATE,
            block_index=0,
        ),
        L2StatusEnum.REQ_OK,
    ),
    (TsL2GetLogRequest(), L2StatusEnum.REQ_OK),
]


@pytest.fixture()
def model_configuration(model_configuration: Dict[str, Any]):
    model_configuration["busy_iter"] = [False]
    yield model_configuration


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _send(model: Tropic01Model, request: L2Request) -> bytes:
    """Send an L2 request; return raw MISO bytes.

    tx[0] = CHIP_STATUS
    tx[1] = init_byte (0x00 — model-specific, not a semantic L2 STATUS)
    """
    model.spi_drive_csn_low()
    tx = model.spi_send(request.to_bytes())
    model.spi_drive_csn_high()
    return tx


def _send_request(model: Tropic01Model) -> bytes:
    """Convenience: send GetInfo(CHIP_ID) and return raw MISO bytes."""
    return _send(
        model,
        TsL2GetInfoRequest(
            object_id=TsL2GetInfoRequest.ObjectIdEnum.CHIP_ID,
            block_index=0,
        ),
    )


def _read_full_response(model: Tropic01Model) -> bytes:
    """Read a complete L2 response; return the header of the first non-busy poll.

    tx[0] = CHIP_STATUS  (READY on the successful GET_RESP)
    tx[1] = L2 STATUS    (REQ_OK for normal single-frame responses)
    tx[2] = LEN field

    Polls with GET_RESP until STATUS ≠ NO_RESP, matching the real ll_receive
    behaviour.  This is necessary because the busy emulation (busy_iter) may
    return NO_RESP transiently even when a response is pending.
    """
    MAX_POLLS = 50

    get_resp = bytes([L2IdFieldEnum.GET_RESP]) + bytes(4)
    for _ in range(MAX_POLLS):
        model.spi_drive_csn_low()
        header = model.spi_send(get_resp)
        if header[1] != L2StatusEnum.NO_RESP:
            break
        model.spi_drive_csn_high()
    else:
        raise TimeoutError(f"Model did not respond after {MAX_POLLS} polls")
    rsp_len = header[2]
    if rsp_len:
        model.spi_send(bytes(rsp_len))
    model.spi_drive_csn_high()
    return header


def _poll_once(model: Tropic01Model) -> bytes:
    """Single GET_RESP poll; return raw MISO bytes.

    tx[0] = CHIP_STATUS
    tx[1] = L2 STATUS (NO_RESP when the response buffer is empty)
    """
    model.spi_drive_csn_low()
    tx = model.spi_send(bytes([L2IdFieldEnum.GET_RESP]) + bytes(4))
    model.spi_drive_csn_high()
    return tx


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_request_write_reports_ready(model: Tropic01Model):
    tx = _send_request(model)

    assert tx[0] == L1ChipStatusFlag.READY
    assert tx[1] == 0x00


def test_get_response_after_consumption_reports_ready_no_resp(
    model_configuration: Dict[str, Any],
):
    """Send L2 Request → Read L2 Response → Get_Response.

    After the response is fully consumed, Get_Response (a bare GET_RESP poll)
    must always return READY=1, STATUS=NO_RESP regardless of the busy
    iterator state.  READY=0 after buffer drain never occurs on the real chip.
    """
    model_configuration["busy_iter"] = [True, False]
    model = Tropic01Model.from_dict(model_configuration)

    tx = _send_request(model)
    assert tx[0] == L1ChipStatusFlag.READY
    assert tx[1] == 0x00

    tx = _read_full_response(model)
    assert tx[0] == L1ChipStatusFlag.READY
    assert tx[1] == L2StatusEnum.REQ_OK

    # Get_Response — the critical poll: must never return READY=0
    tx = _poll_once(model)
    assert tx[0] == L1ChipStatusFlag.READY
    assert tx[1] == L2StatusEnum.NO_RESP


def test_second_request_write_reports_ready(model_configuration: Dict[str, Any]):
    """L2 Request → L2 Response → L2 Request again.

    Checks CHIP_STATUS and L2 STATUS at every key SPI transaction:
      - request send     : tx[0]=READY,  tx[1]=0x00 (model init_byte)
      - response read    : tx[0]=READY,  tx[1]=REQ_OK
      - second request   : tx[0]=READY,  tx[1]=0x00
    """
    model_configuration["busy_iter"] = [True, False]
    model = Tropic01Model.from_dict(model_configuration)

    tx = _send_request(model)
    assert tx[0] == L1ChipStatusFlag.READY
    assert tx[1] == 0x00                     # init_byte during command send

    tx = _read_full_response(model)
    assert tx[0] == L1ChipStatusFlag.READY
    assert tx[1] == L2StatusEnum.REQ_OK      # L2 STATUS in first response

    tx = _send_request(model)
    assert tx[0] == L1ChipStatusFlag.READY
    assert tx[1] == 0x00                     # same init_byte as first send


def test_get_resp_between_two_requests_reports_ready_no_resp(
    model_configuration: Dict[str, Any],
):
    """L2 Request → L2 Response → GET_RESP → L2 Request.

    Checks all four SPI transactions, including the inter-cycle GET_RESP
    that exposed the busy-emulation bug.
    """
    model_configuration["busy_iter"] = [True, False]
    model = Tropic01Model.from_dict(model_configuration)

    tx = _send_request(model)
    assert tx[0] == L1ChipStatusFlag.READY
    assert tx[1] == 0x00

    tx = _read_full_response(model)
    assert tx[0] == L1ChipStatusFlag.READY
    assert tx[1] == L2StatusEnum.REQ_OK

    tx = _poll_once(model)
    assert tx[0] == L1ChipStatusFlag.READY
    assert tx[1] == L2StatusEnum.NO_RESP

    tx = _send_request(model)
    assert tx[0] == L1ChipStatusFlag.READY
    assert tx[1] == 0x00


@pytest.mark.parametrize("n_cycles", [2, 5, 10])
def test_repeated_cycles_get_resp_always_ready_no_resp(
    model_configuration: Dict[str, Any], n_cycles: int
):
    """N consecutive cycles; checks all four transactions each time."""
    model_configuration["busy_iter"] = [True, False]
    model = Tropic01Model.from_dict(model_configuration)

    for _ in range(n_cycles):
        tx = _send_request(model)
        assert tx[0] == L1ChipStatusFlag.READY
        assert tx[1] == 0x00

        tx = _read_full_response(model)
        assert tx[0] == L1ChipStatusFlag.READY
        assert tx[1] == L2StatusEnum.REQ_OK

        tx = _poll_once(model)
        assert tx[0] == L1ChipStatusFlag.READY
        assert tx[1] == L2StatusEnum.NO_RESP


@pytest.mark.parametrize("request_obj, expected_response_status", REQUESTS_TO_TEST)
@pytest.mark.parametrize("n_cycles", [1, 3])
def test_chip_and_l2_status_all_requests(
    model_configuration: Dict[str, Any],
    request_obj: L2Request,
    expected_response_status: L2StatusEnum,
    n_cycles: int
) -> None:
    """CHIP_STATUS and L2 STATUS verified at every transaction for each request type.

    Replaces previous repetitive tests. Verifies that Get_Response always
    returns READY=1, STATUS=NO_RESP after the response buffer is fully drained,
    across all stateless request types the model handles, and checks this
    behavior consistently over multiple cycles.
    """
    model_configuration["busy_iter"] = [True, False]
    model = Tropic01Model.from_dict(model_configuration)

    for _ in range(n_cycles):
        tx = _send(model, request_obj)
        assert tx[0] == L1ChipStatusFlag.READY
        assert tx[1] == 0x00

        tx = _read_full_response(model)
        assert tx[0] == L1ChipStatusFlag.READY
        assert tx[1] == expected_response_status

        tx = _poll_once(model)
        assert tx[0] == L1ChipStatusFlag.READY
        assert tx[1] == L2StatusEnum.NO_RESP
        