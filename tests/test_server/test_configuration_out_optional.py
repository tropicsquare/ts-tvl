"""Tests for the optional `--configuration-out` switch.

`instantiate_model` returns a `save_fn` callback that `run_server`
registers with `atexit` and calls on target reset. Historically the
server always wrote the model configuration to a file
(`./.model_config_save.yaml` by default). Following ETR01SV-100 the
`--configuration-out` argument is optional: when it is not supplied
(`config_out is None`) the save callback must be a no-op and must not
write anything to disk.

See tvl/server/internal.py:instantiate_model and
tvl/server/server.py:get_input_arguments.
"""

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from tvl.server.internal import instantiate_model

CONFIG_FILE = Path(__file__).parent / "test_config.yml"


@patch("tvl.server.internal.dump_configuration")
def test_save_fn_is_noop_when_config_out_is_none(mock_dump, tmp_path: Path) -> None:
    """No file is written and dump is not called when `--configuration-out` is omitted."""
    logger = logging.getLogger("test")

    _model, save_fn = instantiate_model(CONFIG_FILE, None, logger)

    # Invoking the callback (as atexit / target-reset would) must not raise.
    assert save_fn() is None
    # Patching at the call site guards against an accidental write to the CWD,
    # which a `tmp_path`-only check could not detect.
    mock_dump.assert_not_called()
    assert list(tmp_path.iterdir()) == []


def test_save_fn_writes_file_when_config_out_is_given(tmp_path: Path) -> None:
    """The configuration is dumped to a new file when `--configuration-out` is provided."""
    logger = logging.getLogger("test")
    config_out = tmp_path / "model_config_save.yaml"

    _model, save_fn = instantiate_model(CONFIG_FILE, config_out, logger)

    assert not config_out.exists()
    save_fn()
    assert config_out.exists()
    assert config_out.read_text() != ""


def test_save_fn_overwrites_existing_file(tmp_path: Path) -> None:
    """An already existing file is completely overwritten, not appended to."""
    logger = logging.getLogger("test")
    config_out = tmp_path / "model_config_save.yaml"
    config_out.write_text("old_content_that_should_be_overwritten")

    _model, save_fn = instantiate_model(CONFIG_FILE, config_out, logger)

    save_fn()

    assert config_out.exists()
    new_content = config_out.read_text()
    assert new_content != ""
    assert "old_content_that_should_be_overwritten" not in new_content


def test_save_fn_raises_error_on_invalid_directory(tmp_path: Path) -> None:
    """save_fn raises FileNotFoundError when the target directory does not exist.

    Documents that the server does not auto-create parent directories for
    `--configuration-out`; if that behaviour is ever added, this test flips.
    """
    logger = logging.getLogger("test")
    config_out = tmp_path / "nonexistent" / "config.yaml"  # parent dir not created

    _model, save_fn = instantiate_model(CONFIG_FILE, config_out, logger)

    with pytest.raises(FileNotFoundError):
        save_fn()
