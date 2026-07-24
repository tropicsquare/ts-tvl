import io
from dataclasses import dataclass

import yaml

from tvl.targets.model.internal.generic_partition import BaseSlot, GenericPartition
from tvl.typing_utils import HexReprIntEnum


@dataclass
class _Slot(BaseSlot):
    value: int = 0


class _Partition(GenericPartition[_Slot]):
    pass


class _SlotEnum(HexReprIntEnum):
    SLOT_0 = 0x00
    SLOT_1 = 0x01


def test_to_dict_coerces_enum_keys_to_plain_int():
    partition = _Partition()
    partition[_SlotEnum.SLOT_1] = _Slot(value=42)

    result = partition.to_dict()

    (key,) = result.keys()
    assert type(key) is int  # noqa: E721 -- must not stay a HexReprIntEnum
    assert key == _SlotEnum.SLOT_1
    assert result == {1: {"value": 42}}


def test_to_dict_yaml_round_trip_with_enum_keys():
    partition = _Partition()
    partition[_SlotEnum.SLOT_0] = _Slot(value=1)
    partition[_SlotEnum.SLOT_1] = _Slot(value=2)

    buffer = io.StringIO()
    # mirrors tvl.server.configuration._write_to_yaml_file, which uses the
    # default (non-safe) Dumper; an un-coerced enum key would be emitted as
    # an unsafe `!!python/object/apply:...` tag that yaml.safe_load rejects.
    yaml.dump(partition.to_dict(), buffer)
    buffer.seek(0)

    loaded = yaml.safe_load(buffer)
    assert loaded == {0: {"value": 1}, 1: {"value": 2}}
