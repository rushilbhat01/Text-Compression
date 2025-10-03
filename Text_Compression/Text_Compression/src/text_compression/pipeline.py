from __future__ import annotations

import struct
from typing import Tuple

from .lz77 import lz77_compress, lz77_decompress, tokens_to_bytes, bytes_to_tokens
from .huffman import huffman_encode, huffman_decode, build_freqs


MAGIC = b"TZH1"  # Text Zip Huffman v1
VERSION = 1


def compress_bytes(data: bytes, window_size: int = 4096, lookahead_size: int = 18) -> bytes:
    tokens = lz77_compress(data, window_size=window_size, lookahead_size=lookahead_size)
    raw_tokens = tokens_to_bytes(tokens)
    bitstream, freqs = huffman_encode(raw_tokens)

    header = bytearray()
    header += MAGIC
    header += struct.pack(
        ">B I H B I", VERSION, len(data), window_size & 0xFFFF, lookahead_size & 0xFF, len(raw_tokens)
    )
    for f in freqs:
        header += struct.pack(">I", f)
    return bytes(header) + bitstream


def decompress_bytes(blob: bytes) -> bytes:
    mv = memoryview(blob)
    if len(mv) < 4 + 1 + 4 + 2 + 1 + 4 + 256 * 4:
        raise ValueError("Truncated header")
    if mv[:4].tobytes() != MAGIC:
        raise ValueError("Bad magic")
    off = 4
    version, orig_size, window_size, lookahead_size, raw_tokens_len = struct.unpack(
        ">B I H B I", mv[off : off + 1 + 4 + 2 + 1 + 4]
    )
    off += 1 + 4 + 2 + 1 + 4
    if version != VERSION:
        raise ValueError("Unsupported version")
    freqs = list(struct.unpack(">256I", mv[off : off + 256 * 4]))
    off += 256 * 4
    bitstream = mv[off:].tobytes()
    raw_tokens = huffman_decode(bitstream, freqs, raw_tokens_len)
    tokens = bytes_to_tokens(raw_tokens)
    out = lz77_decompress(tokens)
    if len(out) != orig_size:
        raise ValueError("Size mismatch after decompression")
    return out
