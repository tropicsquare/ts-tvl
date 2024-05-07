import os
import random
from binascii import unhexlify
from contextlib import nullcontext
from typing import Any, Callable, ContextManager, NamedTuple, Tuple, Type, cast

import pytest
from _pytest.fixtures import SubRequest

from tvl.targets.model.internal.mac_and_destroy import (
    MACANDD_KEY_LEN,
    MACANDD_KMAC_OUTPUT_LEN,
    MacAndDestroyData,
    MacAndDestroyError,
    MacAndDestroyF1,
    MacAndDestroyF2,
    MacAndDestroyFunc,
    mac_and_destroy_kmac,
)


def test_slot_read():
    macandd_data = MacAndDestroyData()
    slot = random.randint(0, 128)
    assert not macandd_data.slots.items()

    value = macandd_data.read_slot(slot)
    assert len(value) == MACANDD_KMAC_OUTPUT_LEN
    assert macandd_data.slots.items()

    value = macandd_data.read_slot(slot, erase=True)
    assert not macandd_data.slots.items()


def test_key_read():
    macandd_data = MacAndDestroyData()
    slot = random.randint(0, 128)
    assert not macandd_data.keys.items()

    value = macandd_data.read_key(slot)
    assert len(value) == MACANDD_KEY_LEN
    assert macandd_data.keys.items()


def test_slot_write():
    macandd_data = MacAndDestroyData()
    slot = random.randint(0, 128)

    wr_value = os.urandom(MACANDD_KMAC_OUTPUT_LEN)
    macandd_data.write_slot(slot, wr_value)

    rd_value = macandd_data.read_slot(slot)
    assert rd_value == wr_value


def test_key_write():
    macandd_data = MacAndDestroyData()
    slot = random.randint(0, 128)

    wr_value = os.urandom(MACANDD_KEY_LEN)
    macandd_data.write_key(slot, wr_value)

    rd_value = macandd_data.read_key(slot)
    assert rd_value == wr_value


def test_dict():
    macandd_data_dict = {
        "slots":{
            (slot := random.randint(0, 10)):
                (slot_dict := {"value": os.urandom(MACANDD_KMAC_OUTPUT_LEN)})
        },
        "keys":{
            (key := random.randint(0, 10)):
                (key_dict := {"value": os.urandom(MACANDD_KEY_LEN)})
        },
    }

    macandd_data = MacAndDestroyData.from_dict(macandd_data_dict)
    assert macandd_data.to_dict() == macandd_data_dict
    assert macandd_data.slots[slot].to_dict() == slot_dict
    assert macandd_data.keys[key].to_dict() == key_dict


Params = Tuple[
    Callable[[int], int],
    Callable[[int], int],
    ContextManager[Any],
    Callable[[bytes, bytes], bytes],
]


class Vector(NamedTuple):
    func: Type[MacAndDestroyFunc]
    key: bytes
    data: bytes
    context: ContextManager[Any]
    expected_value: bytes


def _identity(x: int) -> int:
    return x


def _plus_one(x: int) -> int:
    return x + 1


def _minus_one(x: int) -> int:
    return x - 1


def _kmac(k: bytes, d: bytes) -> bytes:
    return mac_and_destroy_kmac(k, d)


def _na(k: bytes, d: bytes) -> bytes:
    return b""


@pytest.fixture(params=[MacAndDestroyF1, MacAndDestroyF2])
def macandd_func(request: SubRequest) -> Type[MacAndDestroyFunc]:
    return request.param


@pytest.fixture(
    params=[
        pytest.param(
            (
                _identity,
                _identity,
                nullcontext(),
                _kmac,
            ),
            id="ok",
        ),
        pytest.param(
            (
                _minus_one,
                _identity,
                pytest.raises(MacAndDestroyError),
                _na,
            ),
            id="key_too_short",
        ),
        pytest.param(
            (
                _plus_one,
                _identity,
                pytest.raises(MacAndDestroyError),
                _na,
            ),
            id="key_too_long",
        ),
        pytest.param(
            (
                _identity,
                _minus_one,
                pytest.raises(MacAndDestroyError),
                _na,
            ),
            id="data_too_short",
        ),
        pytest.param(
            (
                _identity,
                _plus_one,
                pytest.raises(MacAndDestroyError),
                _na,
            ),
            id="data_too_long",
        ),
    ],
)
def vector(
    request: SubRequest, macandd_func: Type[MacAndDestroyFunc]
) -> Vector:
    gen_key_len, gen_data_len, ctx, gen_value = cast(Params, request.param)

    return Vector(
        macandd_func,
        key := os.urandom(gen_key_len(MACANDD_KEY_LEN)),
        data := os.urandom(gen_data_len(macandd_func.DATA_LEN)),
        ctx,
        gen_value(key, data),
    )


def test_function(vector: Vector):
    func, key, data, context, expected_value = vector
    with context:
        assert func(key).load(data).compute() == expected_value


def __sv_array_to_py_bytes(x: str) -> bytes:
    lst = x.replace("'{", "").replace("}", "").replace("'h", "").split(", ")
    padded_bytes = (w.zfill(8).encode("ascii") for w in lst)
    reversed_bytes = (bytes(reversed(unhexlify(w))) for w in padded_bytes)
    return b"".join(reversed_bytes)


def __conv_key(x: str) -> bytes:
    return bytes(reversed(unhexlify(x)))


# test vectors from ts-macandd repository, commit 654ea80
# ts_sim_run.py tb_uvm_rtl simple_seq_test
@pytest.mark.parametrize(
    "slot, key_0, data_in_0, data_out_0, key_1, data_in_1, data_out_1",
    [
        pytest.param(
            0x57,
            "a41aadb82048a9100eab020ef0e1508300cb0d32d7462523a1847a64fcd04ff8",
            "'{'h132ad7f2, 'h2bdea9ed, 'hd8f3ddde, 'hdffe90b9, 'h3d807d52, 'h9543ea2d, 'hc00fd15c, 'hcd08c8dc}",
            "'{'h4948fc21, 'h2d193b8, 'h74b0a73f, 'h7d7e730, 'ha7e47560, 'h51eb8ae9, 'hbaff8958, 'ha038fb22}",
            "ca4f2afeaa92aa18cf9ec12096432945597eb575581750672420dbc280558bf1",
            "'{'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'h4948fc21, 'h2d193b8, 'h74b0a73f, 'h7d7e730, 'ha7e47560, 'h51eb8ae9, 'hbaff8958, 'ha038fb22}",
            "'{'h29f4f5f6, 'hf61f6549, 'hb52c567b, 'hfe95ca23, 'h36b009c7, 'ha228b590, 'hf8bc0e03, 'h96119897}",
            id="seed=910587",
        ),
        pytest.param(
            0xAA,
            "fc9736a991b2952f4aefbc7ccd2a60f683c9feea34a2d5fd1690abbb08221e60",
            "'{'h74555f17, 'h5678443a, 'h2fbba592, 'hba780264, 'h8f7c0c83, 'h9f203a11, 'h3f9e021e, 'h292a74ad}",
            "'{'hf2e1805e, 'h892aceef, 'h86aae7af, 'h6f38e9c5, 'hd106fbc6, 'hd548c5a4, 'h3380f44d, 'h669a5881}",
            "95b08fa9a8a9052907e0ce5505496b434a973974a8ba7db6c65c5a9b63b3e53a",
            "'{'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'hf2e1805e, 'h892aceef, 'h86aae7af, 'h6f38e9c5, 'hd106fbc6, 'hd548c5a4, 'h3380f44d, 'h669a5881}",
            "'{'h582e25b2, 'h3347cd7, 'heb244dd5, 'h6bc1d0ee, 'h53375ce5, 'h563eede1, 'h82532fdf, 'hbedc41d8}",
            id="seed=105450",
        ),
        pytest.param(
            0x0F,
            "67fd1a3f93d324e1badb7e981b1a018612411769e5ba48eb2f3c6b76f4a28793",
            "'{'heeee5a27, 'hbb764838, 'hf9fbd103, 'hb6abd593, 'h7ee02be4, 'h4ad84e91, 'hc143aa7, 'hdfb752b1}",
            "'{'h7a3031c9, 'h46d6fdbd, 'h3169182d, 'h634db2a0, 'h996a9bed, 'hec62bb75, 'h6fb4fa19, 'h43af99f4}",
            "a972366b96028ef99197bc9ccb9f4ae56706cb8b1eed2e3ae364933de06895e5",
            "'{'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'hffffffff, 'h7a3031c9, 'h46d6fdbd, 'h3169182d, 'h634db2a0, 'h996a9bed, 'hec62bb75, 'h6fb4fa19, 'h43af99f4}",
            "'{'h8ee5459b, 'hbc323084, 'hef097f9a, 'h95f786ab, 'h226e181c, 'h5ad5aa25, 'hc8fc7451, 'ha9e735ac}",
            id="seed=791961",
        ),
    ],
)
def test(
    slot: int,
    key_0: str,
    data_in_0: str,
    data_out_0: str,
    key_1: str,
    data_in_1: str,
    data_out_1: str,
):
    assert (
        MacAndDestroyF1(__conv_key(key_0))
        .load(__sv_array_to_py_bytes(data_in_0))
        .load(bytes([slot]))
        .compute()
    ) == __sv_array_to_py_bytes(data_out_0)

    assert (
        MacAndDestroyF2(__conv_key(key_1))
        .load(__sv_array_to_py_bytes(data_in_1))
        .load(bytes([slot]))
        .compute()
    ) == __sv_array_to_py_bytes(data_out_1)
