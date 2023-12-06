from typing import List, Union


class MaxResendCountReachedError(Exception):
    pass


class ResponseBuffer:
    """Buffer for saving L2 responses in model"""

    def __init__(self, resend_latest_response_max_count: int) -> None:
        """Initialize the response buffer.

        Args:
            resend_latest_response_max_count (int): maximum number of times
                the latest response can be resent
        """
        self.resend_max_count = max(0, resend_latest_response_max_count)
        self.reset()

    def reset(self) -> None:
        """Reset the buffer."""
        self.latest_response = b""
        self.latest_resend_count = 0
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

    def next(self) -> bytes:
        """Read the next response to send.

        Returns:
            the next response to send
        """
        self.latest_response = self.responses.pop(0)
        self.latest_resend_count = self.resend_max_count
        return self.latest_response

    def latest(self) -> bytes:
        """Get the response previously sent.

        Raises:
            MaxResendCountReachedError: the latest response has already been
                sent the maximum number of times allowed.

        Returns:
            the latest response
        """
        if self.latest_resend_count <= 0:
            raise MaxResendCountReachedError(
                f"Latest response max count reached: {self.resend_max_count}."
            )
        self.latest_resend_count -= 1
        return self.latest_response

    def is_empty(self) -> bool:
        """Assess whether buffer is empty.

        Returns:
            True if the buffer is empty, False otherwise
        """
        return len(self.responses) <= 0
