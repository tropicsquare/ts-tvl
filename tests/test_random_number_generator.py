from tvl.random_number_generator import RandomNumberGenerator


def test_value_is_deterministic_when_initialized_with_not_none():
    rng = RandomNumberGenerator(b"deadbeef")

    v0 = rng.urandom(0)
    v1 = rng.urandom(1)
    v2 = rng.urandom(2)
    v3 = rng.urandom(3)
    v4 = rng.urandom(4)
    v5 = rng.urandom(5)
    v6 = rng.urandom(6)
    v7 = rng.urandom(7)
    v8 = rng.urandom(8)
    v16 = rng.urandom(16)

    assert all(
        (
            len(v0) == 0,
            len(v1) == 1,
            len(v2) == 2,
            len(v3) == 3,
            len(v4) == 4,
            len(v5) == 5,
            len(v6) == 6,
            len(v7) == 7,
            len(v8) == 8,
            len(v16) == 16,
        )
    )
    assert all(
        (
            v0 == b"",
            v1 == b"d",
            v2 == b"de",
            v3 == b"dea",
            v4 == b"dead",
            v5 == b"deadb",
            v6 == b"deadbe",
            v7 == b"deadbee",
            v8 == b"deadbeef",
            v16 == b"deadbeefdeadbeef",
        )
    )


def test_value_is_random_when_initialized_with_none():
    rng = RandomNumberGenerator(None)

    v0 = rng.urandom(0)
    v1 = rng.urandom(1)
    v2 = rng.urandom(2)
    v3 = rng.urandom(3)
    v4 = rng.urandom(4)
    v5 = rng.urandom(5)
    v6 = rng.urandom(6)
    v7 = rng.urandom(7)
    v8 = rng.urandom(8)
    v16 = rng.urandom(16)

    assert all(
        (
            len(v0) == 0,
            len(v1) == 1,
            len(v2) == 2,
            len(v3) == 3,
            len(v4) == 4,
            len(v5) == 5,
            len(v6) == 6,
            len(v7) == 7,
            len(v8) == 8,
            len(v16) == 16,
        )
    )
    assert not all(
        (
            v0 == b"",
            v1 == b"d",
            v2 == b"de",
            v3 == b"dea",
            v4 == b"dead",
            v5 == b"deadb",
            v6 == b"deadbe",
            v7 == b"deadbee",
            v8 == b"deadbeef",
            v16 == b"deadbeefdeadbeef",
        )
    )
