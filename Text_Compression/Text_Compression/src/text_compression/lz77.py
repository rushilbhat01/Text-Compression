from __future__ import annotations

from typing import List, Tuple


Token = Tuple[int, int, int]  # (flag, a, b) where flag=0 literal -> (0, byte, 0); flag=1 match -> (1, offset, length)


def _find_longest_match(data: bytes, pos: int, window_size: int, lookahead_size: int) -> Tuple[int, int]:
    start_window = max(0, pos - window_size)
    best_len = 0
    best_offset = 0
    max_len = min(lookahead_size, len(data) - pos)
    if max_len <= 0:
        return 0, 0
    # naive search: try all offsets in window
    for s in range(start_window, pos):
        length = 0
        while length < max_len and data[s + length] == data[pos + length]:
            length += 1
        if length > best_len:
            best_len = length
            best_offset = pos - s
            if best_len == max_len:
                break
    return best_offset, best_len


def lz77_compress(data: bytes, window_size: int = 4096, lookahead_size: int = 18, min_match: int = 3) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    n = len(data)
    while i < n:
        offset, length = _find_longest_match(data, i, window_size, lookahead_size)
        if length >= min_match and offset > 0:
            tokens.append((1, offset, length))
            i += length
        else:
            tokens.append((0, data[i], 0))
            i += 1
    return tokens


def lz77_decompress(tokens: List[Token]) -> bytes:
    out = bytearray()
    for flag, a, b in tokens:
        if flag == 0:
            out.append(a & 0xFF)
        else:
            offset, length = a, b
            if offset <= 0 or offset > len(out):
                raise ValueError("Invalid offset in token stream")
            start = len(out) - offset
            for _ in range(length):
                out.append(out[start])
                start += 1
    return bytes(out)


def tokens_to_bytes(tokens: List[Token]) -> bytes:
    # Literal: 0x00 byte; Match: 0x01 offset(2 bytes BE) length(1 byte)
    out = bytearray()
    for flag, a, b in tokens:
        if flag == 0:
            out.append(0x00)
            out.append(a & 0xFF)
        else:
            out.append(0x01)
            out.append((a >> 8) & 0xFF)
            out.append(a & 0xFF)
            out.append(b & 0xFF)
    return bytes(out)


def bytes_to_tokens(buf: bytes) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    n = len(buf)
    while i < n:
        t = buf[i]
        i += 1
        if t == 0x00:
            if i >= n:
                raise ValueError("Truncated literal token")
            tokens.append((0, buf[i], 0))
            i += 1
        elif t == 0x01:
            if i + 2 >= n:
                raise ValueError("Truncated match token")
            offset = (buf[i] << 8) | buf[i + 1]
            length = buf[i + 2]
            i += 3
            tokens.append((1, offset, length))
        else:
            raise ValueError("Invalid token tag")
    return tokens
