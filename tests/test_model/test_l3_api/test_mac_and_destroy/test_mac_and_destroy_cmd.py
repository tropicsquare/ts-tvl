import json
from itertools import groupby
from pathlib import Path
import random
from typing import Any, Dict, List, NamedTuple, Tuple, TypedDict

import pytest
from _pytest.fixtures import SubRequest

from tvl.api.l3_api import TsL3MacAndDestroyCommand, TsL3MacAndDestroyResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.utils import chunked

# ts-macandd repository; test-vectors-gen branch; 796df253
_TEST_VECTOR_FILE = Path(__file__).parent / "macandd_test_vectors.json"


class UnprocessedVector(TypedDict):
    slot: str
    chunk: str
    key_word: str
    data_in: str
    data_out: str


class Vector(NamedTuple):
    slot: int
    key_word: bytes
    data: List[Tuple[bytes, bytes]]


def _extract_data(file: Path):

    def _words_to_bytes(data: str):
        return b"".join(bytes(reversed(b)) for b in chunked(bytes.fromhex(data), 4))

    test_vectors: List[UnprocessedVector] = json.loads(file.read_bytes())

    vectors: List[Vector] = []

    for key, iter_group in groupby(test_vectors, lambda x: x["slot"]):
        group = list(iter_group)
        vectors.append(Vector(
            slot=int(key, base=16),
            key_word=_words_to_bytes(group[0]["key_word"]),
            data=list(
                (_words_to_bytes(x["data_in"]), _words_to_bytes(x["data_out"])) for x in group
            ),
        ))
    return vectors


def _get_test_vectors(file: Path, not_slow_nb: int):
    data = _extract_data(file)
    not_slow_indices = set(random.sample(range(len(data)), k=not_slow_nb))
    for i, vector in enumerate(data):
        if i not in not_slow_indices:
            yield pytest.param(vector, marks=pytest.mark.slow, id=str(i))
        else:
            yield pytest.param(vector, id=str(i))


@pytest.fixture(params=_get_test_vectors(_TEST_VECTOR_FILE, 10))
def vector(request: SubRequest) -> Vector:
    return request.param


@pytest.fixture()
def model_configuration(model_configuration: Dict[str, Any], vector: Vector):
    model_configuration["r_macandd_data"] = {
        "keys": {
            1: {"value": 8 * vector.key_word},
            2: {"value": 8 * vector.key_word},
        }
    }
    yield model_configuration


def test(vector: Vector, host: Host):

    for data_in, data_out_exp in vector.data:

        command = TsL3MacAndDestroyCommand(
            slot=vector.slot,
            data_in=data_in,
        )
        result = host.send_command(command)

        assert result.result.value == L3ResultFieldEnum.OK
        assert isinstance(result, TsL3MacAndDestroyResult)
        assert result.data_out.to_bytes() == data_out_exp
