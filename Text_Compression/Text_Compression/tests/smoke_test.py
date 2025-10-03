from __future__ import annotations

from text_compression.pipeline import compress_bytes, decompress_bytes


def test_round_trip_small():
    data = b"abracadabra abracadabra abracadabra\n" * 5
    blob = compress_bytes(data, window_size=1024, lookahead_size=18)
    out = decompress_bytes(blob)
    assert out == data
