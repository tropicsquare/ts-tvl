from functools import reduce
from itertools import chain, product
from math import log2
from operator import xor
from typing import List, Protocol, Reversible, Sequence

from ..utils import chunked
from .conversion import bit, bitlist_to_bytes, ints_to_bitlist

"""Keccak as per https://dx.doi.org/10.6028/NIST.FIPS.202"""


class PaddingFn(Protocol):
    def __call__(self, x: int, m: int) -> List[bit]:
        ...


class PermutationFn(Protocol):
    b: int
    nr: int

    def __call__(self, s: List[List[int]]) -> None:
        ...


ROUND_CONSTANTS = [
    0x0000000000000001,
    0x0000000000008082,
    0x800000000000808A,
    0x8000000080008000,
    0x000000000000808B,
    0x0000000080000001,
    0x8000000080008081,
    0x8000000000008009,
    0x000000000000008A,
    0x0000000000000088,
    0x0000000080008009,
    0x000000008000000A,
    0x000000008000808B,
    0x800000000000008B,
    0x8000000000008089,
    0x8000000000008003,
    0x8000000000008002,
    0x8000000000000080,
    0x000000000000800A,
    0x800000008000000A,
    0x8000000080008081,
    0x8000000000008080,
    0x0000000080000001,
    0x8000000080008008,
]

ROTATION_CONSTANTS = [
    [
        0,
        1,
        62,
        28,
        27,
    ],
    [
        36,
        44,
        6,
        55,
        20,
    ],
    [
        3,
        10,
        43,
        25,
        39,
    ],
    [
        41,
        45,
        15,
        21,
        8,
    ],
    [
        18,
        2,
        61,
        56,
        14,
    ],
]

MASKS = [2**i - 1 for i in range(65)]


class keccak_p:
    def __init__(self, b: int, nr: int) -> None:
        """Keccak-p permutation function as defined in NIST.FIPS.202 3.3

        Args:
            b (int): width of the permutation
            nr (int): number of rounds
        """
        assert b in {25, 50, 100, 200, 400, 800, 1600}
        self.b = b
        self.nr = nr
        self._W = self.b // 25
        self._RND = [x % 2**self._W for x in ROUND_CONSTANTS]
        self._ROT = [[x % self._W for x in row] for row in ROTATION_CONSTANTS]

    def _rol(self, value: int, left: int) -> int:
        top = value >> (x := (self._W - left))
        bot = (value & MASKS[x]) << left
        return bot + top

    def round(self, s: List[List[int]], ir: int) -> None:
        # theta
        c = [reduce(xor, s[x]) for x in range(5)]
        d = [0] * 5
        for x in range(5):
            d[x] = self._rol(c[(x + 1) % 5], 1) ^ c[(x + 4) % 5]
            for y in range(5):
                s[x][y] ^= d[x]

        # rho and pi
        b = [[0] * 5 for _ in range(5)]
        for x, y in product(range(5), range(5)):
            b[y][(2 * x + 3 * y) % 5] = self._rol(s[x][y], self._ROT[y][x])

        # chi
        for x, y in product(range(5), range(5)):
            s[x][y] = b[x][y] ^ ((~b[(x + 1) % 5][y]) & b[(x + 2) % 5][y])

        # iota
        s[0][0] ^= self._RND[ir]

    def __call__(self, s: List[List[int]]) -> None:
        for ir in range(self.nr):
            self.round(s, ir)


def keccak_f(b: int):
    """Keccak-f permutation function as defined in NIST.FIPS.202 3.4

    Args:
        b (int): width of the permutation

    Returns:
        the permutation function keccak-f
    """
    return keccak_p(b, 12 + 2 * int(log2(b / 25)))


class State:
    """
    A keccak state container as defined in NIST.FIPS.202 3.1

    The state is stored as a 5x5 table of integers. Each integer represents
    a lane of the state (constant x, y coordinates).
    """

    @staticmethod
    def bytes_to_lane(data: Reversible[int]) -> int:
        r = 0
        for b in reversed(data):
            r = r << 8 | b
        return r

    def lane_to_bytes(self, lane: int) -> List[int]:
        return [(lane >> b) & 0xFF for b in range(0, self.w, 8)]

    def __init__(self, b: int, r: int) -> None:
        """Create a new Keccak state container

        Args:
            b (int): width of the permutatiom
            r (int): rate
        """
        assert b % 25 == 0
        assert r % 8 == 0

        def __bits_to_bytes(x: int) -> int:
            return (x + 7) // 8

        self.b = b
        self.r = r
        self.b_bytes = __bits_to_bytes(self.b)
        self.r_bytes = __bits_to_bytes(self.r)
        self.c_bytes = __bits_to_bytes(self.b - self.r)
        self.w = b // 25
        self._bitsize = self.w // 8
        self.array = [[0] * 5 for _ in range(5)]

    def __str__(self) -> str:
        def fmt(x: int) -> str:
            return f"{x:0{2 * self._bitsize}x}"

        return "\n".join((" ".join(fmt(x) for x in row) for row in self.array))

    def absorb(self, data: Sequence[int]) -> None:
        """
        Mixes in the given rate-length string to the state.
        """
        assert len(data) <= self.b_bytes
        for (y, x), chunk in zip(
            product(range(5), range(5)), chunked(data, self._bitsize)
        ):
            self.array[x][y] ^= self.bytes_to_lane(chunk)

    def squeeze(self) -> List[int]:
        """
        Returns the rate-length prefix of the state to be output.
        """
        return list(
            chain.from_iterable(
                self.lane_to_bytes(self.array[x][y])
                for y, x in product(range(5), range(5))
            )
        )

    def set_array(self, data: Sequence[int]) -> None:
        """
        Set whole state from byte string, which is assumed
        to be the correct length.
        """
        assert len(data) <= self.b_bytes
        for (y, x), chunk in zip(
            product(range(5), range(5)), chunked(data, self._bitsize)
        ):
            self.array[x][y] = self.bytes_to_lane(chunk)


def sponge(f: PermutationFn, pad: PaddingFn, r: int):
    """Sponge construction as defined in NIST.FIPS.202 4

    Args:
        f (PermutationFn): underlying function
        pad (PaddingFn): padding rule
        r (int): rate
    """

    def call(n: List[bit], d: int) -> List[bit]:
        """Call the sponge function

        Args:
            n (List[bit]): input bit string
            d (int): bit length of the output bit string

        Returns:
            output bit string of length d
        """

        p = n + pad(r, len(n))
        assert len(p) % r == 0

        state = State(f.b, r)

        r_bytes = (r + 7) // 8
        d_bytes = (d + 7) // 8

        for chunk in chunked(bitlist_to_bytes(p), r_bytes):
            state.absorb(chunk)
            f(state.array)

        z: List[int] = []
        while len(z) < d_bytes:
            z += state.squeeze()[:r_bytes]
            f(state.array)
        if len(z) != d_bytes:
            z = z[:d_bytes]

        return ints_to_bitlist(z)

    return call


def pad10s1(x: int, m: int) -> List[bit]:
    """Multi-rate padding as defined in NIST.FIPS.202 5.1

    Args:
        x (int): positive integer
        m (int): non-negative integer

    Returns:
        p such as m + len(p) is a positive multiple of x
    """
    j = (-m - 2) % x
    return [bit(1)] + [bit(0)] * j + [bit(1)]


def keccak(b: int):
    """KECCAK sponge as defined in NIST.FIPS.202 6.2

    Args:
        b (int): width of the permutation
    """

    def call(r: int):
        return sponge(keccak_f(b), pad10s1, r)

    return call


def keccak_c(c: int):
    """KECCAK[c] sponge as defined in NIST.FIPS.202 6.2

    Args:
        c (int): capacity
    """

    def call(n: List[bit], d: int) -> List[bit]:
        return keccak(b := 1600)(b - c)(n, d)

    return call


def shake256(m: List[bit], d: int) -> List[bit]:
    """SHAKE256 hash function as defined in NIST.FIPS.202 6.2

    Args:
        m (List[bit]): message
        d (int): digest length

    Returns:
        digest
    """
    return keccak_c(512)(m + [bit(1), bit(1), bit(1), bit(1)], d)
