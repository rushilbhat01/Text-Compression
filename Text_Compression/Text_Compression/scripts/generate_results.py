from __future__ import annotations

import csv
import os
import pathlib
import random
import time
from typing import List, Tuple

import sys


def _add_src_to_path() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))


_add_src_to_path()
from text_compression.pipeline import compress_bytes, decompress_bytes  # noqa: E402


def gen_random_bytes(n: int, seed: int = 1234) -> bytes:
    rnd = random.Random(seed)
    return bytes(rnd.getrandbits(8) for _ in range(n))


def load_file_if_exists(path: pathlib.Path) -> bytes | None:
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def run_case(name: str, data: bytes) -> Tuple[str, int, int, float, float, float]:
    t0 = time.perf_counter()
    blob = compress_bytes(data)
    t1 = time.perf_counter()
    out = decompress_bytes(blob)
    t2 = time.perf_counter()
    assert out == data, f"Round-trip mismatch for {name}"
    in_size = len(data)
    out_size = len(blob)
    ratio = (out_size / in_size) if in_size else 1.0
    comp_ms = (t1 - t0) * 1000.0
    decomp_ms = (t2 - t1) * 1000.0
    return name, in_size, out_size, ratio, comp_ms, decomp_ms


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    results_dir = root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    cases: List[Tuple[str, bytes]] = []
    cases.append(("quick_brown_fox_x200", (b"The quick brown fox jumps over the lazy dog. " * 200)))
    cases.append(("abracadabra_x2000", (b"abracadabra " * 2000)))
    cases.append(("random_64k", gen_random_bytes(64 * 1024)))

    readme_data = load_file_if_exists(root / "README.md")
    if readme_data is not None:
        cases.append(("README_md", readme_data))

    results: List[Tuple[str, int, int, float, float, float]] = []
    for name, data in cases:
        results.append(run_case(name, data))

    # Write CSV
    csv_path = results_dir / "results.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "input_bytes", "compressed_bytes", "ratio", "compress_ms", "decompress_ms"])
        for row in results:
            w.writerow(row)

    # Write Markdown summary
    md_path = results_dir / "results.md"
    lines = [
        "# Compression Results",
        "",
        "This report summarizes LZ77 + Huffman compression performance on a few sample corpora.",
        "",
        "| name | input bytes | compressed bytes | ratio | compress ms | decompress ms |",
        "|------|-------------:|-----------------:|------:|------------:|--------------:|",
    ]
    for name, in_b, out_b, ratio, c_ms, d_ms in results:
        lines.append(f"| {name} | {in_b} | {out_b} | {ratio:.3f} | {c_ms:.2f} | {d_ms:.2f} |")
    lines.append("")
    lines.append("Notes:")
    lines.append("- Ratios < 1 are better (smaller compressed size). Random data is typically incompressible.")
    lines.append("- Times are wall-clock on your machine and will vary across runs.")

    md_path.write_text("\n".join(lines))

    print(f"Wrote {csv_path} and {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
