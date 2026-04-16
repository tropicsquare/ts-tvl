"""Smoke tests for the TCP transport to tvl.server."""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterator

import pytest
import yaml

from tvl.api.l2_api import TsL2GetInfoRequest
from tvl.constants import (
    CERTIFICATE_BLOCK_SIZE,
    CHIP_ID_SIZE,
    L2StatusEnum,
    RISCV_FW_VERSION_SIZE,
    SPECT_FW_VERSION_SIZE,
)
from tvl.host.host import Host
from tvl.host.simple_target_driver import SimpleTargetDriver
from tvl.server.tcp_client import TCPTropicProtocol
from tvl.server.tcp_connection import TCP_DEFAULT_ADDRESS, TCP_DEFAULT_PORT

CONFIG_FILE = Path(__file__).parent / "test_config.yml"


@pytest.fixture(scope="module")
def model_config() -> Dict[str, Any]:
    """Load the ground-truth model config for assertion comparisons."""
    with open(CONFIG_FILE, "r") as fd:
        return yaml.safe_load(fd)


@pytest.fixture(scope="module")
def server_process() -> Iterator["subprocess.Popen[str]"]:
    """Start the model server subprocess for the whole test module."""
    cmd = [
        sys.executable, "-m", "tvl.server.server", "tcp",
        "--address", TCP_DEFAULT_ADDRESS,
        "--port", str(TCP_DEFAULT_PORT),
        "--configuration", str(CONFIG_FILE),
    ]
    logger = logging.getLogger("server_launcher")
    logger.info("Starting model server: %s", " ".join(cmd))

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    try:
        yield process
    finally:
        if process.poll() is None:
            process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        # 0 = clean exit, -SIGTERM = expected when we terminate() it
        if process.returncode not in (0, -15):
            sys.stderr.write(f"server stdout:\n{stdout}\n")
            sys.stderr.write(f"server stderr:\n{stderr}\n")


@pytest.fixture
def tcp_host(server_process: "subprocess.Popen[str]") -> Host:
    """Build a Host wired to the server via TCP."""
    protocol = TCPTropicProtocol(server_process=server_process)
    return Host(target_driver=SimpleTargetDriver(target=protocol))


GET_INFO_CASES = [
    pytest.param(
        TsL2GetInfoRequest.ObjectIdEnum.CHIP_ID,
        "chip_id",
        CHIP_ID_SIZE,
        id="chip_id",
    ),
    pytest.param(
        TsL2GetInfoRequest.ObjectIdEnum.RISCV_FW_VERSION,
        "riscv_fw_version",
        RISCV_FW_VERSION_SIZE,
        id="riscv_fw_version",
    ),
    pytest.param(
        TsL2GetInfoRequest.ObjectIdEnum.SPECT_FW_VERSION,
        "spect_fw_version",
        SPECT_FW_VERSION_SIZE,
        id="spect_fw_version",
    ),
    pytest.param(
        TsL2GetInfoRequest.ObjectIdEnum.X509_CERTIFICATE,
        "x509_certificate",
        CERTIFICATE_BLOCK_SIZE,
        id="x509_certificate",
    ),
]


@pytest.mark.parametrize("object_id, cfg_key, size", GET_INFO_CASES)
def test_get_info_over_tcp(
    tcp_host: Host,
    model_config: Dict[str, Any],
    object_id: TsL2GetInfoRequest.ObjectIdEnum,
    cfg_key: str,
    size: int,
) -> None:
    """Every GetInfoReq round-trips through TCP and matches the config."""
    with tcp_host:
        response = tcp_host.send_request(
            TsL2GetInfoRequest(object_id=object_id, block_index=0)
        )
    assert response.status.value == L2StatusEnum.REQ_OK
    assert response.object.to_bytes() == model_config[cfg_key][:size]
