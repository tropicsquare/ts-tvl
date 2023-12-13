# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from typing import Optional, Union

from ...constants import L2StatusEnum, L3ResultFieldEnum


class _ProcessingError(Exception):
    """
    Internal exception used by the model.
    Exceptions from this type are used to manage processing errors in a clean
    way inside the model and should not be propagated outside of it.
    """


class L2ProcessingError(_ProcessingError):
    """Internal L2 error"""

    STATUS: int

    """L2 status that should be sent when such an exception occurs"""

    def __init__(
        self, arg: Union[str, Exception] = "", *, status: Optional[int] = None
    ) -> None:
        super().__init__(arg)
        if status is None:
            status = self.STATUS
        self.status = status


class L2ProcessingErrorContinue(L2ProcessingError):
    STATUS = L2StatusEnum.REQ_CONT


class L2ProcessingErrorHandshake(L2ProcessingError):
    STATUS = L2StatusEnum.HSK_ERR


class L2ProcessingErrorNoSession(L2ProcessingError):
    STATUS = L2StatusEnum.NO_SESSION


class L2ProcessingErrorTag(L2ProcessingError):
    STATUS = L2StatusEnum.TAG_ERR


class L2ProcessingErrorUnknownRequest(L2ProcessingError):
    STATUS = L2StatusEnum.UNKNOWN_REQ


class L2ProcessingErrorGeneric(L2ProcessingError):
    STATUS = L2StatusEnum.GEN_ERR


class L3ProcessingError(_ProcessingError):
    """Internal L3 error"""

    RESULT: int
    """L3 result that should be sent when such an exception occurs"""

    def __init__(
        self, arg: Union[str, Exception] = "", *, result: Optional[int] = None
    ) -> None:
        super().__init__(arg)
        if result is None:
            result = self.RESULT
        self.result = result


class L3ProcessingErrorUnauthorized(L3ProcessingError):
    RESULT = L3ResultFieldEnum.UNAUTHORIZED


class L3ProcessingErrorFail(L3ProcessingError):
    RESULT = L3ResultFieldEnum.FAIL


class L3ProcessingErrorInvalidCmd(L3ProcessingError):
    RESULT = L3ResultFieldEnum.INVALID_CMD


class ResendLastResponse(_ProcessingError):
    pass
