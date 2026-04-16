"""Test helper: run tvl.server.server with an injected delay in model init.

Reads MODEL_INIT_DELAY (seconds, float) from the environment and sleeps that
long inside `tvl.server.internal.instantiate_model`, widening the window
between the TCP listen socket opening and the model being ready to handle
requests.

Used by test_startup_race.py to deterministically exercise the race where
the server accepts TCP connections before the model is instantiated.
"""

import os
import time

from tvl.server import internal

_original_instantiate = internal.instantiate_model


def _delayed_instantiate_model(config_in, config_out, logger):
    delay = float(os.environ.get("MODEL_INIT_DELAY", "0"))
    if delay > 0:
        logger.info(
            "MODEL_INIT_DELAY=%s: sleeping before model instantiation", delay
        )
        time.sleep(delay)
    return _original_instantiate(config_in, config_out, logger)


# Replace the module attribute AND the default of run_server, because
# run_server captured instantiate_model as a default arg at def time.
internal.instantiate_model = _delayed_instantiate_model
internal.run_server.__defaults__ = (_delayed_instantiate_model,)


if __name__ == "__main__":
    from tvl.server.server import main

    main()
