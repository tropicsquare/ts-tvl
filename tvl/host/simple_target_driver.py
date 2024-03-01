# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, List, Optional

from typing_extensions import Self

from ..protocols import TropicProtocol
from .protocols import LLSendL2RequestFn, LLSendL3CommandFn


class SimpleTargetDriver:
    def __init__(
        self,
        target: TropicProtocol,
        *,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        if logger is None:
            logger = logging.getLogger(self.__class__.__name__.lower())
        self.logger = logger
        self.target = target

    def __enter__(self) -> Self:
        self.target.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self.target.__exit__()

    def send_l2_request(self, fn: LLSendL2RequestFn, data: bytes) -> bytes:
        return fn(data, self.target, self.logger)

    def send_l3_command(self, fn: LLSendL3CommandFn, data: List[bytes]) -> List[bytes]:
        return fn(data, self.target, self.logger)
