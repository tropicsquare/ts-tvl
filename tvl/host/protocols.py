import logging
from typing import Any, List, Optional, Protocol, Type

from typing_extensions import Self

from ..messages.l2_messages import L2Request
from ..messages.l3_messages import L3Command
from ..protocols import TropicProtocol


class LLSendL2RequestFn(Protocol):
    """Used for sending and receiving data to and from one Tropic chip"""

    def __call__(
        self,
        data: bytes,
        target: TropicProtocol,
        logger: logging.Logger,
    ) -> bytes:
        ...


class LLSendL3CommandFn(Protocol):
    """Used for receiving data from one Tropic chip"""

    def __call__(
        self,
        cmd_chunks: List[bytes],
        target: TropicProtocol,
        logger: logging.Logger,
    ) -> List[bytes]:
        ...


class FunctionFactory(Protocol):
    def create_ll_l2_fn(
        self, __type: Type[L2Request], __id: Optional[int] = None
    ) -> LLSendL2RequestFn:
        ...

    def create_ll_l3_fn(
        self, __type: Type[L3Command], __id: Optional[int] = None
    ) -> LLSendL3CommandFn:
        ...


class TargetDriver(Protocol):
    """Executes the functions on the target(s) that it embeds"""

    logger: logging.Logger

    def __enter__(self) -> Self:
        ...

    def __exit__(self, *args: Any) -> None:
        ...

    def send_l2_request(self, fn: LLSendL2RequestFn, data: bytes) -> bytes:
        ...

    def send_l3_command(self, fn: LLSendL3CommandFn, data: List[bytes]) -> List[bytes]:
        ...
