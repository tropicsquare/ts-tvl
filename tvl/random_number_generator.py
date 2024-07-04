# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import os
from itertools import cycle, islice
from typing import Optional


class RandomNumberGenerator:
    """
    RNG which can be initialized with a value.
    When reading random bytes from the rng, the debug random value, if set,
    will be repeated as many times as it needs to fill the buffer.
    Otherwise random numbers will be output.
    This mechanism allows for control over the generation of random numbers
    during tests in debug mode.
    """

    def __init__(self, debug_random_value: Optional[bytes] = None) -> None:
        """Initialize the random number generator.

        Args:
            debug_random_value (bytes, optional): debug random value.
                Defaults to None.
        """
        self.debug_random_value = debug_random_value

    def urandom(self, size: int, /, *, swap_endianness: bool = False) -> bytes:
        """Read random bytes from the random number generator.

        Args:
            size (int): the number of bytes to generate.
            swap_endianness (bool): revert bytes of the debug random value if used.
                Defaults to False.

        Returns:
            an array of random bytes
        """
        if (debug_random_value := self.debug_random_value) is None:
            return os.urandom(size)

        if swap_endianness:
            debug_random_value = reversed(debug_random_value)

        return bytes(islice(cycle(debug_random_value), size))
