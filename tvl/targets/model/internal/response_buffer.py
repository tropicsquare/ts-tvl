from typing import List, Union


class ResponseBuffer:
    """Buffer for saving L2 responses in model"""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Reset the buffer."""
        self.latest_response = b""
        self.responses: List[bytes] = []

    def add(self, x: Union[bytes, List[bytes]]) -> None:
        """Add one or several new responses to the buffer.

        Args:
            x (Union[bytes, List[bytes]]): the responses to output
        """
        if isinstance(x, list):
            self.responses.extend(x)
        else:
            self.responses.append(x)

    def requeue(self, data: bytes, previous_latest: bytes) -> None:
        """Re-insert data at the front of the buffer and restore latest.

        Used when a SPI transaction is aborted (CSN high) before the
        response was fully transferred.  The ``next()`` call that loaded
        *data* also overwrote ``latest_response``, so we must roll that
        back to *previous_latest* — the value it had before the aborted
        transaction started.

        Args:
            data (bytes): the response data to re-queue
            previous_latest (bytes): the latest_response value to restore
        """
        self.responses.insert(0, data)
        self.latest_response = previous_latest

    def next(self) -> bytes:
        """Read the next response to send.

        Returns:
            the next response to send
        """
        self.latest_response = self.responses.pop(0)
        return self.latest_response

    def latest(self) -> bytes:
        """Get the response previously sent.

        Returns:
            the latest response
        """
        return self.latest_response

    def is_empty(self) -> bool:
        """Assess whether buffer is empty.

        Returns:
            True if the buffer is empty, False otherwise
        """
        return len(self.responses) <= 0
