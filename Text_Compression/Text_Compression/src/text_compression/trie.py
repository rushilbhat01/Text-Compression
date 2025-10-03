from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TrieNode:
    left: Optional["TrieNode"] = None
    right: Optional["TrieNode"] = None
    symbol: Optional[int] = None  # leaf holds a byte value 0..255


class PrefixTrie:
    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, bits: int, bitlen: int, symbol: int) -> None:
        node = self.root
        for i in range(bitlen - 1, -1, -1):
            bit = (bits >> i) & 1
            if bit == 0:
                if node.left is None:
                    node.left = TrieNode()
                node = node.left
            else:
                if node.right is None:
                    node.right = TrieNode()
                node = node.right
        node.symbol = symbol

    def decode_next(self, reader_bit_getter) -> int:
        """Traverse until a leaf is reached using reader_bit_getter() -> int in {0,1}."""
        node = self.root
        while node.symbol is None:
            bit = reader_bit_getter()
            node = node.left if bit == 0 else node.right
            if node is None:
                raise ValueError("Invalid Huffman bitstream: reached dead end")
        return node.symbol
