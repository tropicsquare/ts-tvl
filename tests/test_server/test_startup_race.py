"""Regression test for the TCP startup race.

The TCP server must not accept connections until the model has been
instantiated. Historically `TCPConnection.__init__` calls `create_server()`
which binds + listens immediately, while `run_server` only instantiates the
model afterwards. A client connecting in that window completes the TCP
handshake and then hangs on `recv` until the server finally reaches
`accept()`.

This test injects an artificial delay into model instantiation via the
`slow_server_main.py` helper and asserts that no client can connect to the
server during that window. The test FAILS today (bug present) and will pass
once the fix is in place (typically: defer `create_server()` until after
`_instantiate_target()` returns in `run_server`).

See tvl/server/tcp_connection.py and tvl/server/internal.py:run_server.
"""

import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterator, Tuple

import pytest

CONFIG_FILE = Path(__file__).parent / "test_config.yml"
HELPER = Path(__file__).parent / "slow_server_main.py"

# Use a dedicated port so this test can never collide with the smoke-test
# module (which uses TCP_DEFAULT_PORT == 28992).
RACE_TEST_PORT = 28993
RACE_TEST_ADDRESS = "127.0.0.1"

MODEL_INIT_DELAY_S = 2.0


@pytest.fixture
def slow_server() -> Iterator[Tuple["subprocess.Popen[str]", float]]:
    """Spawn the server subprocess with a 2 s model-instantiation delay.

    Yields (process, spawn_time) so the test can measure elapsed time from
    the moment the subprocess was launched.
    """
    cmd = [
        sys.executable, str(HELPER), "tcp",
        "--address", RACE_TEST_ADDRESS,
        "--port", str(RACE_TEST_PORT),
        "--configuration", str(CONFIG_FILE),
    ]
    env = {**__import__("os").environ, "MODEL_INIT_DELAY": str(MODEL_INIT_DELAY_S)}
    spawn_time = time.monotonic()
    process = subprocess.Popen(
        cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    try:
        yield process, spawn_time
    finally:
        if process.poll() is None:
            process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        if process.returncode not in (0, -15):
            sys.stderr.write(f"server stdout:\n{stdout}\n")
            sys.stderr.write(f"server stderr:\n{stderr}\n")


def _time_until_connect_succeeds(
    address: str, port: int, deadline: float
) -> float:
    """Return the monotonic time at which a TCP connect first succeeds.

    Polls tightly; raises AssertionError if `deadline` elapses first.
    """
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        try:
            sock.connect((address, port))
            sock.close()
            return time.monotonic()
        except (ConnectionRefusedError, socket.timeout, OSError):
            sock.close()
        if time.monotonic() >= deadline:
            pytest.fail(
                f"Server never started accepting connections on "
                f"{address}:{port} within the allotted window."
            )
        time.sleep(0.02)


def test_tcp_server_does_not_accept_before_model_ready(slow_server) -> None:
    """A client must not be able to connect before the model is instantiated.

    With the bug present, `create_server()` binds+listens in
    `TCPConnection.__init__` before `run_server` instantiates the model, so
    connect succeeds almost immediately after subprocess startup, well
    before `MODEL_INIT_DELAY_S` has elapsed. This assertion catches that.
    """
    process, spawn_time = slow_server

    first_connect = _time_until_connect_succeeds(
        RACE_TEST_ADDRESS,
        RACE_TEST_PORT,
        deadline=spawn_time + MODEL_INIT_DELAY_S * 5,
    )
    elapsed = first_connect - spawn_time

    # Allow a small tolerance below the delay to absorb scheduler jitter.
    min_expected = MODEL_INIT_DELAY_S * 0.7
    assert elapsed >= min_expected, (
        f"TCP connect succeeded {elapsed:.2f}s after server spawn, but model "
        f"instantiation takes ~{MODEL_INIT_DELAY_S:.1f}s. The listen socket "
        f"is being opened before the model is ready to serve requests — see "
        f"create_server() in TCPConnection.__init__ "
        f"(tvl/server/tcp_connection.py). Expected connect to be refused "
        f"for at least {min_expected:.1f}s."
    )
