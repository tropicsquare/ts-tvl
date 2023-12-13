# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from tempfile import NamedTemporaryFile

import pytest


@pytest.fixture
def temp_file():
    named_temporary_file = NamedTemporaryFile()
    yield named_temporary_file.name


@pytest.fixture(autouse=True, scope="function")
def add_return():
    # Pretty print
    print()


def pytest_assertrepr_compare(op: str, left: object, right: object):
    if isinstance(left, int) and isinstance(right, int):
        return [f"{hex(left)} {op} {hex(right)}"]
