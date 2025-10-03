from __future__ import annotations

import argparse
import os
import sys

from .pipeline import compress_bytes, decompress_bytes


def _default_out_path(in_path: str, mode: str) -> str:
    if mode == "compress":
        return in_path + ".tzh"
    else:
        return in_path[:-4] if in_path.endswith(".tzh") else in_path + ".out"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LZ77 + Huffman compressor")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_c = sub.add_parser("compress", help="Compress a file")
    p_c.add_argument("input", help="Input file path")
    p_c.add_argument("-o", "--output", help="Output file path")
    p_c.add_argument("--window", type=int, default=4096, help="LZ77 window size")
    p_c.add_argument("--lookahead", type=int, default=18, help="LZ77 lookahead size")

    p_d = sub.add_parser("decompress", help="Decompress a file")
    p_d.add_argument("input", help="Input .tzh file path")
    p_d.add_argument("-o", "--output", help="Output file path")

    args = parser.parse_args(argv)

    if args.cmd == "compress":
        with open(args.input, "rb") as f:
            data = f.read()
        blob = compress_bytes(data, window_size=args.window, lookahead_size=args.lookahead)
        out_path = args.output or _default_out_path(args.input, "compress")
        with open(out_path, "wb") as f:
            f.write(blob)
        print(f"Wrote {out_path} ({len(blob)} bytes) from {len(data)} bytes")
        return 0

    elif args.cmd == "decompress":
        with open(args.input, "rb") as f:
            blob = f.read()
        data = decompress_bytes(blob)
        out_path = args.output or _default_out_path(args.input, "decompress")
        with open(out_path, "wb") as f:
            f.write(data)
        print(f"Wrote {out_path} ({len(data)} bytes)")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
