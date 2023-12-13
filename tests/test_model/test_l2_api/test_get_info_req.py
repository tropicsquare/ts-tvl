# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os

import pytest

from tvl.api.l2_api import TsL2GetInfoReqRequest, TsL2GetInfoReqResponse
from tvl.constants import L2StatusEnum
from tvl.host.host import Host
from tvl.messages.l2_messages import L2Response

from ..base_test import BaseTest
from ..utils import one_of, one_outside

_X509_CERTIFICATE = os.urandom(512)
_CHIP_ID = os.urandom(128)
_RISCV_FW_VERSION = os.urandom(4)
_SPECT_FW_VERSION = os.urandom(4)


def _send_no_check(host: Host, object_id: int, block_index: int) -> L2Response:
    request = TsL2GetInfoReqRequest(object_id=object_id, block_index=block_index)
    return host.send_request(request)


def _send(host: Host, object_id: int, block_index: int) -> TsL2GetInfoReqResponse:
    response = _send_no_check(host, object_id, block_index)
    assert response.status.value == L2StatusEnum.REQ_OK
    assert isinstance(response, TsL2GetInfoReqResponse)
    return response


class TestGetInfoReq(BaseTest):
    CONFIGURATION = {
        "model": {
            "x509_certificate": _X509_CERTIFICATE,
            "chip_id": _CHIP_ID,
            "riscv_fw_version": _RISCV_FW_VERSION,
            "spect_fw_version": _SPECT_FW_VERSION,
        }
    }

    @pytest.mark.parametrize(
        "block_index, indices",
        [
            pytest.param(
                (b := TsL2GetInfoReqRequest.BlockIndexEnum.DATA_CHUNK_0_127),
                slice(0, 128),
                id=str(b),
            ),
            pytest.param(
                (b := TsL2GetInfoReqRequest.BlockIndexEnum.DATA_CHUNK_128_255),
                slice(128, 256),
                id=str(b),
            ),
            pytest.param(
                (b := TsL2GetInfoReqRequest.BlockIndexEnum.DATA_CHUNK_256_383),
                slice(256, 384),
                id=str(b),
            ),
            pytest.param(
                (b := TsL2GetInfoReqRequest.BlockIndexEnum.DATA_CHUNK_384_511),
                slice(384, 512),
                id=str(b),
            ),
        ],
    )
    def test_x509_certificate(self, host: Host, block_index: int, indices: slice):
        response = _send(
            host,
            TsL2GetInfoReqRequest.ObjectIdEnum.X509_CERTIFICATE,
            block_index,
        )
        assert response.object.to_bytes() == _X509_CERTIFICATE[indices]

    @pytest.mark.parametrize("block_index", TsL2GetInfoReqRequest.BlockIndexEnum)
    def test_chip_id(self, host: Host, block_index: int):
        response = _send(
            host,
            TsL2GetInfoReqRequest.ObjectIdEnum.CHIP_ID,
            block_index,
        )
        assert response.object.to_bytes() == _CHIP_ID

    @pytest.mark.parametrize("block_index", TsL2GetInfoReqRequest.BlockIndexEnum)
    def test_chip_riscv_fw_version(self, host: Host, block_index: int):
        response = _send(
            host,
            TsL2GetInfoReqRequest.ObjectIdEnum.RISCV_FW_VERSION,
            block_index,
        )
        assert response.object.to_bytes() == _RISCV_FW_VERSION

    @pytest.mark.parametrize("block_index", TsL2GetInfoReqRequest.BlockIndexEnum)
    def test_chip_spect_rom_id(self, host: Host, block_index: int):
        response = _send(
            host,
            TsL2GetInfoReqRequest.ObjectIdEnum.SPECT_FW_VERSION,
            block_index,
        )
        assert response.object.to_bytes() == _SPECT_FW_VERSION

    def test_invalid_object_id(self, host: Host):
        response = _send_no_check(
            host=host,
            object_id=one_outside(TsL2GetInfoReqRequest.ObjectIdEnum),
            block_index=one_of(TsL2GetInfoReqRequest.BlockIndexEnum),
        )
        assert response.status.value == L2StatusEnum.GEN_ERR
        assert response.data_field_bytes == b""

    @pytest.mark.parametrize(
        "object_id, expected_status",
        [
            pytest.param(
                (oid := TsL2GetInfoReqRequest.ObjectIdEnum.X509_CERTIFICATE),
                L2StatusEnum.GEN_ERR,
                id=str(oid),
            ),
            pytest.param(
                (oid := TsL2GetInfoReqRequest.ObjectIdEnum.CHIP_ID),
                L2StatusEnum.REQ_OK,
                id=str(oid),
            ),
            pytest.param(
                (oid := TsL2GetInfoReqRequest.ObjectIdEnum.RISCV_FW_VERSION),
                L2StatusEnum.REQ_OK,
                id=str(oid),
            ),
            pytest.param(
                (oid := TsL2GetInfoReqRequest.ObjectIdEnum.SPECT_FW_VERSION),
                L2StatusEnum.REQ_OK,
                id=str(oid),
            ),
        ],
    )
    def test_invalid_block_index(
        self, host: Host, object_id: int, expected_status: int
    ):
        response = _send_no_check(
            host=host,
            object_id=object_id,
            block_index=one_outside(TsL2GetInfoReqRequest.BlockIndexEnum),
        )
        assert response.status.value == expected_status
