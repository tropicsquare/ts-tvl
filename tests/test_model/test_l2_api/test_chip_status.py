from typing import Any, Dict, Tuple

import pytest

from tvl.api.l2_api import TsL2GetInfoRequest
from tvl.constants import L1ChipStatusFlag, L2IdFieldEnum, L2StatusEnum
from tvl.targets.model.tropic01_model import Tropic01Model


@pytest.fixture()
def model_configuration(model_configuration: Dict[str, Any]):
    model_configuration["busy_iter"] = [False]
    yield model_configuration


def _send_request(model: Tropic01Model) -> bytes:
    request = TsL2GetInfoRequest(
        object_id=TsL2GetInfoRequest.ObjectIdEnum.CHIP_ID,
        block_index=0,
    )

    model.spi_drive_csn_low()
    tx = model.spi_send(request.to_bytes())
    model.spi_drive_csn_high()
    return tx


def _read_full_response(model: Tropic01Model) -> Tuple[bytes, bytes]:
    get_resp = bytes([L2IdFieldEnum.GET_RESP]) + bytes(4)

    model.spi_drive_csn_low()
    header = model.spi_send(get_resp)
    rsp_len = header[2]
    payload = model.spi_send(bytes(rsp_len)) if rsp_len else b""
    model.spi_drive_csn_high()
    return header, payload


def test_request_write_reports_ready(model: Tropic01Model):
    tx = _send_request(model)

    assert tx[0] == L1ChipStatusFlag.READY


def test_get_response_after_consumption_reports_ready_no_resp(
    model_configuration: Dict[str, Any]
):
    model_configuration["busy_iter"] = [False, True]
    model = Tropic01Model.from_dict(model_configuration)

    _send_request(model)
    _read_full_response(model)

    model.spi_drive_csn_low()
    tx = model.spi_send(bytes([L2IdFieldEnum.GET_RESP]) + bytes(4))
    model.spi_drive_csn_high()

    assert tx[0] == L1ChipStatusFlag.READY
    assert tx[1] == L2StatusEnum.NO_RESP
