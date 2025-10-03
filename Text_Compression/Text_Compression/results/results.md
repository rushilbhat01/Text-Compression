# Compression Results

This report summarizes LZ77 + Huffman compression performance on a few sample corpora.

| name | input bytes | compressed bytes | ratio | compress ms | decompress ms |
|------|-------------:|-----------------:|------:|------------:|--------------:|
| quick_brown_fox_x200 | 9000 | 2023 | 0.225 | 3.51 | 7.73 |
| abracadabra_x2000 | 24000 | 2896 | 0.121 | 7.26 | 14.25 |
| random_64k | 65536 | 82700 | 1.262 | 23593.71 | 507.84 |
| README_md | 1967 | 2422 | 1.231 | 74.51 | 9.81 |

Notes:
- Ratios < 1 are better (smaller compressed size). Random data is typically incompressible.
- Times are wall-clock on your machine and will vary across runs.