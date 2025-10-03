from __future__ import annotations

from typing import Iterable, List


class BitWriter:
    def __init__(self) -> None:
        self._buffer: int = 0
        self._bit_count: int = 0
        self._out: bytearray = bytearray()

    def write_bits(self, value: int, nbits: int) -> None:
        if nbits < 0:
            raise ValueError("nbits must be >= 0")
        if nbits == 0:
            return
        if value < 0 or value >= (1 << nbits):
            raise ValueError("value has more bits than nbits")
        self._buffer = (self._buffer << nbits) | value
        self._bit_count += nbits
        while self._bit_count >= 8:
            self._bit_count -= 8
            byte = (self._buffer >> self._bit_count) & 0xFF
            self._out.append(byte)
            self._buffer &= (1 << self._bit_count) - 1

    def write_bytes(self, data: bytes | bytearray | Iterable[int]) -> None:
        if self._bit_count != 0:
            # align to next byte
            self.write_bits(0, 8 - self._bit_count)
        if isinstance(data, (bytes, bytearray)):
            self._out.extend(data)
        else:
            self._out.extend(int(b) & 0xFF for b in data)

    def getvalue(self) -> bytes:
        if self._bit_count:
            self.write_bits(0, 8 - self._bit_count)
        return bytes(self._out)


class BitReader:
    def __init__(self, data: bytes) -> None:
        self._data = memoryview(data)
        self._pos = 0
        self._buffer = 0
        self._bit_count = 0

    def read_bits(self, nbits: int) -> int:
        if nbits < 0:
            raise ValueError("nbits must be >= 0")
        while self._bit_count < nbits:
            if self._pos >= len(self._data):
                raise EOFError("Not enough bits")
            self._buffer = (self._buffer << 8) | self._data[self._pos]
            self._pos += 1
            self._bit_count += 8
        self._bit_count -= nbits
        val = (self._buffer >> self._bit_count) & ((1 << nbits) - 1)
        self._buffer &= (1 << self._bit_count) - 1
        return val

    def read_bytes(self, n: int) -> bytes:
        if self._bit_count % 8 != 0:
            # byte align
            _ = self.read_bits(self._bit_count % 8)
        if self._pos + n > len(self._data):
            raise EOFError("Not enough bytes")
        start = self._pos
        self._pos += n
        return self._data[start:self._pos].tobytes()

    def remaining_bytes(self) -> bytes:
        if self._bit_count % 8 != 0:
            _ = self.read_bits(self._bit_count % 8)
        return self._data[self._pos:].tobytes()
