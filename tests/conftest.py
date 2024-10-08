# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from contextlib import suppress

from _pytest.config import Config
from _pytest.terminal import TerminalReporter

from tvl.constants import L2IdFieldEnum, L2StatusEnum, L3ResultFieldEnum
from tvl.messages.message import BaseMessage


def pytest_assertrepr_compare(op: str, left: object, right: object):
    if isinstance(left, int):
        if isinstance(right, (L2IdFieldEnum, L2StatusEnum, L3ResultFieldEnum)):
            return [f"{left:#x} {op} {right!r}"]

        if isinstance(right, int):
            return [f"{left:#x} {op} {right:#x}"]

    if isinstance(left, BaseMessage) or isinstance(right, BaseMessage):
        return [f"{left} {op} {right}"]


def pytest_terminal_summary(terminalreporter: TerminalReporter, config: Config):
    with suppress(ValueError):
        seed = config.getoption("randomly_seed")
        terminalreporter.ensure_newline()
        terminalreporter.section("Reproducibility seed", sep="-", bold=True)
        terminalreporter.line(
            f"Reproduce using --randomly-seed={seed} (or --randomly-seed=last if you just ran this session)",
            bold=True,
        )
