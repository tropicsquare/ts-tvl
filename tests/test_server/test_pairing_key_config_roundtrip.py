"""Round trip of the dumped configuration through the pairing key partition.

The model server loads a configuration with `--configuration` and dumps the
final state of the model with `--configuration-out`. That dump must be usable
as the input of a subsequent run.

Invalidated and blank pairing key slots hold no value - `PairingKeySlot`
switched from the 0xFF.../0x00... sentinel values to a `state` attribute - and
are dumped as `value: !!binary ""`, which used to be rejected on reload because
`PairingKeySlotModel.value` was constrained to exactly KEY_SIZE bytes.

See tvl/server/configuration.py:load_configuration and :dump_configuration.
"""

import logging
from pathlib import Path
from typing import Dict, Set

import yaml

from tvl.server.configuration import dump_configuration, load_configuration
from tvl.targets.model.internal.pairing_keys import SlotState
from tvl.targets.model.tropic01_model import Tropic01Model

CONFIG_FILE = Path(__file__).parent / "test_config.yml"

LOG = logging.getLogger(__name__)


def _instantiate(config_in: Path) -> Tropic01Model:
    return Tropic01Model.from_dict(load_configuration(config_in, LOG))


def _dump(model: Tropic01Model, config_out: Path) -> Path:
    dump_configuration(config_out, model.to_dict(), LOG)
    return config_out


def _dumped_slots(config_out: Path) -> Dict[int, Dict[str, object]]:
    return yaml.safe_load(config_out.read_text())["i_pairing_keys"]


def _written_slots(model: Tropic01Model) -> Set[int]:
    return {idx for idx, slot in model.i_pairing_keys.items() if slot.is_valid()}


def test_written_slots_roundtrip(tmp_path: Path) -> None:
    """The unmodified configuration is dumped and reloaded unchanged."""
    model = _instantiate(CONFIG_FILE)
    assert (slots := _written_slots(model))

    reloaded = _instantiate(_dump(model, tmp_path / "config_new.yml"))

    for slot in slots:
        assert reloaded.i_pairing_keys[slot].state is SlotState.WRITTEN
        assert reloaded.i_pairing_keys[slot].value == model.i_pairing_keys[slot].value


def test_invalidated_slot_roundtrip(tmp_path: Path) -> None:
    """A slot invalidated by TsL3PairingKeyInvalidateCommand can be reloaded."""
    model = _instantiate(CONFIG_FILE)
    assert (slots := _written_slots(model))
    for slot in slots:
        model.i_pairing_keys[slot].invalidate()

    config_out = _dump(model, tmp_path / "config_new.yml")

    # The dump holds no value for the invalidated slots.
    dumped = _dumped_slots(config_out)
    for slot in slots:
        assert dumped[slot] == {"state": "invalid", "value": b""}

    reloaded = _instantiate(config_out)

    for slot in slots:
        assert reloaded.i_pairing_keys[slot].state is SlotState.INVALID
        assert reloaded.i_pairing_keys[slot].value == b""


def test_blank_slot_roundtrip(tmp_path: Path) -> None:
    """A blank slot ends up in the dump and can be reloaded.

    The handshake looks the slot up in the partition, and the partition being a
    defaultdict this materializes a blank slot - see tropic01_l2_api_impl.py.
    """
    model = _instantiate(CONFIG_FILE)
    slot = max(model.i_pairing_keys) + 1
    _ = model.i_pairing_keys[slot]

    config_out = _dump(model, tmp_path / "config_new.yml")
    assert _dumped_slots(config_out)[slot] == {"state": "blank", "value": b""}

    reloaded = _instantiate(config_out)

    assert reloaded.i_pairing_keys[slot].state is SlotState.BLANK
    assert reloaded.i_pairing_keys[slot].value == b""


def test_repeated_roundtrips_are_stable(tmp_path: Path) -> None:
    """Dumping and reloading again does not alter the configuration."""
    model = _instantiate(CONFIG_FILE)
    for slot in _written_slots(model):
        model.i_pairing_keys[slot].invalidate()
    _ = model.i_pairing_keys[max(model.i_pairing_keys) + 1]

    first = _dump(model, tmp_path / "config_1.yml")
    second = _dump(_instantiate(first), tmp_path / "config_2.yml")

    assert _dumped_slots(second) == _dumped_slots(first)
