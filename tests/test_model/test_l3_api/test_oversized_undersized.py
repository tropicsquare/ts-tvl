"""
Tests for firmware v2.0.0 behavior (ts-tr01-app: main/cmd_l3.c,
main/ts_l3.c): an L3 command whose payload size does not match the API
spec is not answered with an encrypted L3 RESULT=FAIL — the chip
responds at the L2 layer with STATUS=GEN_ERR and closes the secure
session.
"""
from typing import List, Tuple

import pytest

from tvl.api.l2_api import TsL2EncryptedCmdRequest
from tvl.api.l3_api import L3Enum
from tvl.constants import MAX_L2_FRAME_DATA_LEN, L2StatusEnum
from tvl.host.host import Host
from tvl.messages.l2_messages import L2Response
from tvl.messages.l3_messages import L3EncryptedPacket
from tvl.targets.model.tropic01_model import Tropic01Model
from tvl.utils import split_data


def _send_raw_l3(
    host: Host, model: Tropic01Model, raw_l3: bytes
) -> Tuple[List[L2Response], int]:
    """
    Push raw L3 command bytes through the secure channel, bypassing
    client-side API validation so we can feed the model an
    oversized/undersized payload. Returns every L2 response the model
    produced across all L2 chunks plus the number of L2 chunks sent.
    """
    ciphertext = host.session.encrypt_command(raw_l3)
    encrypted_packet = L3EncryptedPacket.from_encrypted(ciphertext)
    l2_chunks = list(
        split_data(encrypted_packet.to_bytes(), chunk_size=MAX_L2_FRAME_DATA_LEN)
    )
    assert l2_chunks, "expected at least one L2 chunk"

    responses: List[L2Response] = []
    for chunk in l2_chunks:
        request = TsL2EncryptedCmdRequest(l3_chunk=chunk)
        raw = model.process_input(request.to_bytes())
        # On the final chunk error path the model emits two L2 frames:
        # the REQ_OK ack of the last received chunk, then GEN_ERR (which
        # in firmware is delivered on the next GET_RESP).
        raw_list = raw if isinstance(raw, list) else [raw]
        responses.extend(
            L2Response.with_length(len(r)).from_bytes(r) for r in raw_list
        )
    return responses, len(l2_chunks)


def _assert_gen_err_and_session_closed(
    responses: List[L2Response],
    model: Tropic01Model,
    host: Host,
    n_l2_chunks: int,
) -> None:
    # Per firmware: every chunk-receive request including the last is
    # acknowledged at L2 (REQ_CONT for non-final, REQ_OK for the final
    # chunk because cmd_l3_rx_done is true at that point). The GEN_ERR
    # is then queued by cmd_l3_task and fetched on the next GET_RESP.
    # The model returns it as the trailing item of the last chunk's
    # response list, which the spi_fsm hands back on GET_RESP.
    assert len(responses) == n_l2_chunks + 1, (
        f"expected {n_l2_chunks} chunk acks + 1 GEN_ERR, "
        f"got {len(responses)} responses: "
        f"{[hex(r.status.value) for r in responses]}"
    )
    for r in responses[: n_l2_chunks - 1]:
        assert r.status.value == L2StatusEnum.REQ_CONT
    assert responses[n_l2_chunks - 1].status.value == L2StatusEnum.REQ_OK
    assert responses[-1].status.value == L2StatusEnum.GEN_ERR
    # Firmware closes the session on this error; the model must mirror.
    assert not model.session.is_session_valid()
    assert model.command_buffer.is_empty()
    # Host session is independent from model state; unchanged.
    assert host.session.is_session_valid()


# --- fixed-size commands --------------------------------------------------
# TsL3RConfigReadCommand: id(1) + address(2) = 3 bytes exactly.

@pytest.mark.parametrize(
    "raw_l3",
    [
        pytest.param(bytes([L3Enum.R_CONFIG_READ]) + b"\x00\x00\x00", id="oversized_by_1"),
        pytest.param(bytes([L3Enum.R_CONFIG_READ]) + b"\x00" * 10, id="oversized_by_10"),
        pytest.param(bytes([L3Enum.R_CONFIG_READ]) + b"\x00", id="undersized_by_1"),
        pytest.param(bytes([L3Enum.R_CONFIG_READ]), id="undersized_missing_payload"),
    ],
)
def test_fixed_size_mismatch_returns_gen_err(
    host: Host, model: Tropic01Model, raw_l3: bytes
):
    responses, n_chunks = _send_raw_l3(host, model, raw_l3)
    _assert_gen_err_and_session_closed(responses, model, host, n_chunks)


# --- variable-size commands -----------------------------------------------
# TsL3PingCommand: id(1) + data_in(0..4096)  -> oversize beyond max_size.
# TsL3RMemDataWriteCommand: id(1) + udata_slot(2) + padding(1) + data(1..475)
#   -> undersize below min and oversize above max.

def test_ping_oversized_returns_gen_err(host: Host, model: Tropic01Model):
    # PING max data_in is 4096 bytes. Send 4097 -> out of spec.
    raw_l3 = bytes([L3Enum.PING]) + b"\xab" * 4097
    responses, n_chunks = _send_raw_l3(host, model, raw_l3)
    _assert_gen_err_and_session_closed(responses, model, host, n_chunks)


def test_r_mem_data_write_undersized_returns_gen_err(
    host: Host, model: Tropic01Model
):
    # Minimum valid length is id(1)+slot(2)+padding(1)+data_min(1) = 5.
    # Send 4 bytes -> undersized.
    raw_l3 = bytes([L3Enum.R_MEM_DATA_WRITE]) + b"\x00\x00\x00"
    responses, n_chunks = _send_raw_l3(host, model, raw_l3)
    _assert_gen_err_and_session_closed(responses, model, host, n_chunks)


def test_r_mem_data_write_oversized_returns_gen_err(
    host: Host, model: Tropic01Model
):
    # Maximum valid length is id(1)+slot(2)+padding(1)+data_max(475) = 479.
    # Send 480 bytes -> oversized by 1.
    raw_l3 = bytes([L3Enum.R_MEM_DATA_WRITE]) + b"\x00\x00\x00" + b"\xcd" * 476
    responses, n_chunks = _send_raw_l3(host, model, raw_l3)
    _assert_gen_err_and_session_closed(responses, model, host, n_chunks)
