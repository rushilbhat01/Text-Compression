Text Compression using LZ77 and Huffman Coding

Lossless compression pipeline that first applies LZ77 (LZSS-style) tokenization and then Huffman-codes the token byte stream. A prefix trie is used to decode Huffman codes efficiently.

Features
- Lempel–Ziv '77 (LZ77) variant with a sliding window and greedy longest-match parsing
- Token stream encoding using a compact literal/match format
- Huffman coding constructed via a heap-based priority queue
- Prefix trie used for storing and traversing Huffman codes (decoding)
- Simple container format with header and frequency table for decoder reconstruction
- Clean Python implementation with CLI

Container format
- Magic: `TZH1`
- Version: 1 byte (currently `1`)
- Original size: 4 bytes (uint32, big-endian)
- Window size: 2 bytes (uint16, big-endian)
- Lookahead size: 1 byte (uint8)
- Token stream length: 4 bytes (uint32)
- Huffman frequency table: 256 x 4 bytes (uint32, big-endian)
- Bitstream: Huffman-coded token stream bits, padded to a full byte

Token format (pre-Huffman)
For each token:
- Literal: `0x00 <byte>`
- Match: `0x01 <offset:2 bytes BE> <length:1 byte>`

Constraints:
- `offset` in [1, 65535]
- `length` in [3, 255] (threshold is 3; shorter matches become literals)

CLI
- Compress: `python -m text_compression.cli compress <input> [-o OUTPUT] [--window 4096] [--lookahead 18]`
- Decompress: `python -m text_compression.cli decompress <input> [-o OUTPUT]`

If output is omitted:
- compress: writes `<input>.tzh`
- decompress: removes trailing `.tzh` or appends `.out`

Development
Run via module path (no install required):

```bash
PYTHONPATH=src python -m text_compression.cli compress sample.txt
PYTHONPATH=src python -m text_compression.cli decompress sample.txt.tzh
```

Notes
- The implementation favors clarity and correctness over extreme speed.
- The naive search in LZ77 is O(n * window * lookahead). For large inputs, consider optimizing with suffix arrays/trees or hash chains.

Results
- See `results/results.md` for a quick benchmark summary, with the raw data in `results/results.csv`.
- Regenerate by running:

```bash
python3 scripts/generate_results.py
```
