"""Text Compression using LZ77 and Huffman Coding.

Modules:
- lz77: LZ77 (LZSS-style) tokenization and detokenization
- huffman: Huffman coding with heap-based priority queue
- trie: Prefix trie for decoding codes
- bitio: Bit-level reader and writer utilities
- pipeline: Container format and file-level compress/decompress
- cli: Command-line interface
"""

__all__ = [
    "lz77",
    "huffman",
    "trie",
    "bitio",
    "pipeline",
]
