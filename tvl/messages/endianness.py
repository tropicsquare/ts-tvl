# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from typing import Literal


class Endianness:
    """Manage endianness of messages"""

    def __init__(self) -> None:
        self._endianness: Literal["little", "big"] = "little"

    def set(self, endianness: Literal["little", "big"]) -> None:
        self._endianness = endianness

    def get(self) -> Literal["little", "big"]:
        return self._endianness

    @property
    def fmt(self) -> str:
        """Format character for data conversion to bytes"""
        return {
            "little": "<",
            "big": ">",
        }[self._endianness]


endianness = Endianness()
"""Endianess of messages upon their conversion to bytes"""
