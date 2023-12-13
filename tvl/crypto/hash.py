# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import crcmod.predefined

_crc16 = crcmod.predefined.mkPredefinedCrcFun("crc-16-buypass")


def crc16(__data: bytes, /) -> int:
    return _crc16(__data)
