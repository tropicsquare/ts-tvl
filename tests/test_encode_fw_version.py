import pytest

from tvl.constants import encode_fw_version


@pytest.mark.parametrize(
    "version_str, expected_bytes",
    [
        pytest.param("0.0.0", b"\x00\x00\x00\x00", id="zero"),
        pytest.param("1.0.0", b"\x00\x00\x00\x01", id="1.0.0"),
        pytest.param("2.0.0", b"\x00\x00\x00\x02", id="2.0.0"),
        pytest.param("1.1.0", b"\x00\x00\x01\x01", id="1.1.0"),
        pytest.param("0.9.2", b"\x00\x02\x09\x00", id="0.9.2"),
        pytest.param("255.255.255", b"\x00\xff\xff\xff", id="max_components"),
        pytest.param("1.0.0-1", b"\x02\x00\x00\x01", id="1_commit"),
        pytest.param("1.0.0-127", b"\xfe\x00\x00\x01", id="max_commits"),
        pytest.param("1.0.0-dirty", b"\x01\x00\x00\x01", id="dirty"),
        pytest.param("1.0.0-127-dirty", b"\xff\x00\x00\x01", id="max_commits_dirty"),
        pytest.param(
            "2.0.0-5-gabcdef-dirty", b"\x0b\x00\x00\x02", id="full_git_describe"
        ),
        pytest.param("v2.0.0", b"\x00\x00\x00\x02", id="v_prefix"),
    ],
)
def test_encode_fw_version(version_str: str, expected_bytes: bytes):
    assert encode_fw_version(version_str) == expected_bytes


@pytest.mark.parametrize(
    "version_str",
    [
        pytest.param("256.0.0", id="major_overflow"),
        pytest.param("0.256.0", id="minor_overflow"),
        pytest.param("0.0.256", id="patch_overflow"),
        pytest.param("1.0.0-128", id="commits_overflow"),
        pytest.param("not_a_version", id="invalid_format"),
        pytest.param("", id="empty_string"),
    ],
)
def test_encode_fw_version_invalid(version_str: str):
    with pytest.raises(ValueError):
        encode_fw_version(version_str)
