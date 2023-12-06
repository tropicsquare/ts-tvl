from typing import List


class CommandBuffer:
    """Buffer for stacking chunks of commands and issuing the full command"""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Reset the buffer."""
        self.total_size = 0
        self.received_size = 0
        self.chunks: List[bytes] = []

    def initialize(self, expected_total_size: int) -> None:
        """Prepare the buffer for reception of the command.

        Args:
            expected_total_size (int): the total size of the command
        """
        self.total_size = expected_total_size

    def add_chunk(self, data: bytes) -> None:
        """Add a new chunk to the stack.

        Args:
            data (bytes): part of the command
        """
        self.received_size += len(data)
        if (diff := self.received_size - self.total_size) <= 0:
            self.chunks.append(data)
        else:
            self.chunks.append(data[:-diff])
            self.received_size -= diff

    def is_command_incomplete(self) -> bool:
        """Assess whether some bytes can be added.

        Returns:
            True if the command is incomplete, else False
        """
        return not self.is_empty() and self.received_size < self.total_size

    def is_empty(self) -> bool:
        """Assess whether the buffer is empty.

        Returns:
            True if the buffer is empty, else False
        """
        return self.total_size <= 0

    def get_raw_command(self) -> bytes:
        """Issue the full serialized command.

        Returns:
            the full command
        """
        raw_command = b"".join(self.chunks)
        self.reset()
        return raw_command
