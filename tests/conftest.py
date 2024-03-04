# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0


def pytest_assertrepr_compare(op: str, left: object, right: object):
    if isinstance(left, int) and isinstance(right, int):
        return [f"{hex(left)} {op} {hex(right)}"]
