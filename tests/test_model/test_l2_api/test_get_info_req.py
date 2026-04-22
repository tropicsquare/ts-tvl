import os
from typing import Any, Callable, Dict, Iterator

import pytest

from tvl.api.l2_api import TsL2GetInfoRequest, TsL2GetInfoResponse
from tvl.constants import (
    L2StatusEnum,
    RISCV_FW_VERSION_DEFAULT,
    SPECT_FW_VERSION_DEFAULT,
    encode_fw_version,
)
from tvl.host.host import Host

from ..utils import one_of, one_outside

_X509_CERTIFICATE = os.urandom(512)
_CHIP_ID = os.urandom(128)
_RISCV_FW_VERSION = os.urandom(4)
_SPECT_FW_VERSION = os.urandom(4)


@pytest.fixture()
def model_configuration(model_configuration: Dict[str, Any]):
    model_configuration.update(
        {
            "x509_certificate": _X509_CERTIFICATE,
            "chip_id": _CHIP_ID,
            "riscv_fw_version": _RISCV_FW_VERSION,
            "spect_fw_version": _SPECT_FW_VERSION,
        }
    )
    yield model_configuration


def _valid_block_index() -> Iterator[int]:
    yield from range(30)


def _get_padded_certificate_chunk(block_index: int) -> bytes:
    chunk = _X509_CERTIFICATE[block_index * 128 : (block_index + 1) * 128]
    return b"\x00" * (128 - len(chunk)) + chunk


@pytest.mark.parametrize("block_index", _valid_block_index())
@pytest.mark.parametrize(
    "object_id, expected_data_fn",
    [
        pytest.param(
            oid := TsL2GetInfoRequest.ObjectIdEnum.X509_CERTIFICATE,
            _get_padded_certificate_chunk,
            id=str(oid),
        ),
        pytest.param(oid := TsL2GetInfoRequest.ObjectIdEnum.CHIP_ID, lambda x: _CHIP_ID, id=str(oid)),  # type: ignore
        pytest.param(oid := TsL2GetInfoRequest.ObjectIdEnum.RISCV_FW_VERSION, lambda x: _RISCV_FW_VERSION, id=str(oid)),  # type: ignore
        pytest.param(oid := TsL2GetInfoRequest.ObjectIdEnum.SPECT_FW_VERSION, lambda x: _SPECT_FW_VERSION, id=str(oid)),  # type: ignore
    ],
)
def test(
    host: Host,
    block_index: int,
    object_id: int,
    expected_data_fn: Callable[[int], bytes],
):
    request = TsL2GetInfoRequest(object_id=object_id, block_index=block_index)
    response = host.send_request(request)

    assert response.status.value == L2StatusEnum.REQ_OK
    assert isinstance(response, TsL2GetInfoResponse)
    assert response.object.to_bytes() == expected_data_fn(block_index)


def test_invalid_object_id(host: Host):
    request = TsL2GetInfoRequest(
        object_id=one_outside(TsL2GetInfoRequest.ObjectIdEnum),
        block_index=one_of(_valid_block_index()),
    )
    response = host.send_request(request)

    assert response.status.value == L2StatusEnum.GEN_ERR
    assert response.data_field_bytes == b""


@pytest.mark.parametrize(
    "object_id, expected_status",
    [
        pytest.param(
            (oid := TsL2GetInfoRequest.ObjectIdEnum.X509_CERTIFICATE),
            L2StatusEnum.GEN_ERR,
            id=str(oid),
        ),
        pytest.param(
            (oid := TsL2GetInfoRequest.ObjectIdEnum.CHIP_ID),
            L2StatusEnum.REQ_OK,
            id=str(oid),
        ),
        pytest.param(
            (oid := TsL2GetInfoRequest.ObjectIdEnum.RISCV_FW_VERSION),
            L2StatusEnum.REQ_OK,
            id=str(oid),
        ),
        pytest.param(
            (oid := TsL2GetInfoRequest.ObjectIdEnum.SPECT_FW_VERSION),
            L2StatusEnum.REQ_OK,
            id=str(oid),
        ),
    ],
)
def test_invalid_block_index(host: Host, object_id: int, expected_status: int):
    request = TsL2GetInfoRequest(
        object_id=object_id, block_index=one_outside(_valid_block_index())
    )
    response = host.send_request(request)

    assert response.status.value == expected_status


def _query_fw_version(configuration, object_id, version_override=None):
    """Create a model (optionally overriding a version) and query GetInfo."""
    from tvl.targets.model.tropic01_model import Tropic01Model

    if version_override is not None:
        configuration["model"][object_id.name.lower()] = version_override
    model = Tropic01Model.from_dict(configuration["model"])
    with Host.from_dict(configuration["host"]).set_target(model) as host:
        request = TsL2GetInfoRequest(object_id=object_id, block_index=0)
        response = host.send_request(request)
    assert response.status.value == L2StatusEnum.REQ_OK
    assert isinstance(response, TsL2GetInfoResponse)
    return response.object.to_bytes()


@pytest.mark.parametrize(
    "object_id, expected_version",
    [
        pytest.param(
            TsL2GetInfoRequest.ObjectIdEnum.RISCV_FW_VERSION,
            RISCV_FW_VERSION_DEFAULT,
            id="riscv_fw_version",
        ),
        pytest.param(
            TsL2GetInfoRequest.ObjectIdEnum.SPECT_FW_VERSION,
            SPECT_FW_VERSION_DEFAULT,
            id="spect_fw_version",
        ),
    ],
)
def test_default_fw_version(configuration, object_id, expected_version):
    """Test that the model returns valid default firmware versions."""
    assert _query_fw_version(configuration, object_id) == expected_version


@pytest.mark.parametrize(
    "object_id, version_str",
    [
        pytest.param(
            TsL2GetInfoRequest.ObjectIdEnum.RISCV_FW_VERSION,
            "3.1.4",
            id="riscv_fw_version",
        ),
        pytest.param(
            TsL2GetInfoRequest.ObjectIdEnum.SPECT_FW_VERSION,
            "2.5.1",
            id="spect_fw_version",
        ),
        pytest.param(
            TsL2GetInfoRequest.ObjectIdEnum.RISCV_FW_VERSION,
            "2.0.0-5-gabcdef-dirty",
            id="riscv_fw_version_dirty_with_commits",
        ),
        pytest.param(
            TsL2GetInfoRequest.ObjectIdEnum.SPECT_FW_VERSION,
            "1.2.0-dirty",
            id="spect_fw_version_dirty",
        ),
        pytest.param(
            TsL2GetInfoRequest.ObjectIdEnum.RISCV_FW_VERSION,
            "2.0.0-12",
            id="riscv_fw_version_commits_since_tag",
        ),
    ],
)
def test_fw_version_from_string(configuration, object_id, version_str):
    """Test that firmware versions can be configured as human-readable strings."""
    assert _query_fw_version(configuration, object_id, version_str) == encode_fw_version(version_str)
