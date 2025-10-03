from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .bitio import BitReader, BitWriter
from .trie import PrefixTrie


def build_freqs(data: bytes) -> List[int]:
    freqs = [0] * 256
    for b in data:
        freqs[b] += 1
    # avoid all-zero edge case by ensuring at least one symbol present
    if sum(freqs) == 0:
        freqs[0] = 1
    return freqs


@dataclass(order=True)
class _Node:
    freq: int
    symbol: int | None = field(default=None, compare=False)
    left: "_Node | None" = field(default=None, compare=False)
    right: "_Node | None" = field(default=None, compare=False)


def _build_tree(freqs: List[int]) -> _Node:
    heap: List[_Node] = []
    for sym, f in enumerate(freqs):
        if f > 0:
            heap.append(_Node(f, sym))
    if not heap:
        heap.append(_Node(1, 0))
    heapq.heapify(heap)
    if len(heap) == 1:
        # duplicate node to ensure non-zero code length
        single = heap[0]
        heapq.heappush(heap, _Node(single.freq, single.symbol))
    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        parent = _Node(n1.freq + n2.freq, None, n1, n2)
        heapq.heappush(heap, parent)
    return heap[0]


def _gen_codes(node: _Node, prefix: int, length: int, out: Dict[int, Tuple[int, int]]) -> None:
    if node.symbol is not None:
        out[node.symbol] = (prefix if length > 0 else 0, max(length, 1))
        return
    assert node.left is not None and node.right is not None
    _gen_codes(node.left, (prefix << 1) | 0, length + 1, out)
    _gen_codes(node.right, (prefix << 1) | 1, length + 1, out)


def build_codes(freqs: List[int]) -> Dict[int, Tuple[int, int]]:
    root = _build_tree(freqs)
    codes: Dict[int, Tuple[int, int]] = {}
    _gen_codes(root, 0, 0, codes)
    return codes


def huffman_encode(raw: bytes, freqs: List[int] | None = None) -> Tuple[bytes, List[int]]:
    if freqs is None:
        freqs = build_freqs(raw)
    codes = build_codes(freqs)
    bw = BitWriter()
    for b in raw:
        code, clen = codes[b]
        bw.write_bits(code, clen)
    return bw.getvalue(), freqs


def build_decode_trie(freqs: List[int]) -> PrefixTrie:
    codes = build_codes(freqs)
    trie = PrefixTrie()
    for sym, (bits, length) in codes.items():
        trie.insert(bits, length, sym)
    return trie


def huffman_decode(bitstream: bytes, freqs: List[int], expected_len: int) -> bytes:
    reader = BitReader(bitstream)
    trie = build_decode_trie(freqs)

    def next_bit() -> int:
        return reader.read_bits(1)

    out = bytearray()
    while len(out) < expected_len:
        sym = trie.decode_next(next_bit)
        out.append(sym)
    return bytes(out)
