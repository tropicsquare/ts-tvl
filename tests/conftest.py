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
