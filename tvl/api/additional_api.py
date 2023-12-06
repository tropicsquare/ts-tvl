from typing import Iterator

from ..messages.datafield import U8Array, params
from ..messages.l2_messages import L2Request, L2Response
from ..utils import chunked
from .l2_api import TsL2EncryptedCmdReqRequest, TsL2EncryptedCmdReqResponse

"""
This file defines an additional L2-message pair to handle splitted commands
and results more conveniently in both the model and the host.
"""

MAX_L2_FRAME_DATA_LEN = 255
ENCRYPTED_PACKET_MAX_SIZE = 2 + 4096 + 16


class L2EncryptedCmdChunk(L2Request, id=TsL2EncryptedCmdReqRequest.ID):
    encrypted_cmd: U8Array[params(min_size=0, max_size=ENCRYPTED_PACKET_MAX_SIZE)]


class L2EncryptedResChunk(L2Response, id=TsL2EncryptedCmdReqResponse.ID):
    encrypted_res: U8Array[params(min_size=0, max_size=ENCRYPTED_PACKET_MAX_SIZE)]


def split_data(
    data: bytes, *, chunk_size: int = MAX_L2_FRAME_DATA_LEN
) -> Iterator[bytes]:
    """Split raw data into several chunks.

    Args:
        data (bytes): data to split
        chunk_size (int, optional): Maximal size of an individual chunk.
            Defaults to MAX_L2_FRAME_DATA_LEN.

    Yields:
        the chunks
    """
    yield from (bytes(chunk) for chunk in chunked(data, chunk_size))
