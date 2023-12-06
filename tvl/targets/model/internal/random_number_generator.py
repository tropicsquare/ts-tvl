import os
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

    def get_random_bytes(self, length: int) -> bytes:
        """Read random bytes from the random number generator.

        Args:
            length (int): the number of bytes to read

        Returns:
            an array of random values
        """
        if not self.debug_random_value:
            return os.urandom(length)
        word_number = (length // len(self.debug_random_value)) + 1
        return (self.debug_random_value * word_number)[:length]
