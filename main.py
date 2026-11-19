#!/usr/bin/env python3
"""Ship the vendored infographic as the competition entry.

Copies ``entry.png`` (built by ``draw_news.py``) into the harness output
directory and verifies the copy byte-for-byte, so a truncated or corrupted
write can never be submitted silently.

Stdlib only. No network, no randomness: two runs produce identical output.
"""

import hashlib
import os
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024

MAX_BYTES = 1_048_576  # 1 MiB entry cap
FALLBACK_OUT = Path("/output")


def check_png(path: Path) -> None:
    """Reject anything that is not a 1024x1024 PNG before copying.

    Reads the 8-byte magic and the IHDR chunk (width/height as big-endian
    uint32 at bytes 16..24) with the stdlib only.
    """
    head = path.read_bytes()[:33]
    if head[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file (bad magic)")
    if len(head) < 24 or head[12:16] != b"IHDR":
        raise ValueError("not a PNG file (missing IHDR)")
    width, height = struct.unpack(">II", head[16:24])
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise ValueError(
            f"wrong dimensions: {width}x{height}, "
            f"expected {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}"
        )


def output_path() -> Path:
    """Output dir from $MAKEFUN_OUTPUT_DIR, else /output."""
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    return (Path(raw) if raw else FALLBACK_OUT) / "entry.png"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not SOURCE.is_file():
        print(f"missing source image: {SOURCE}", file=sys.stderr)
        return 1

    size = SOURCE.stat().st_size
    if size > MAX_BYTES:
        print(f"entry.png too large: {size} bytes (max {MAX_BYTES})",
              file=sys.stderr)
        return 1
    if size == 0:
        print("entry.png is empty", file=sys.stderr)
        return 1

    try:
        check_png(SOURCE)
    except ValueError as exc:
        print(f"entry.png rejected: {exc}", file=sys.stderr)
        return 1

    expected = digest(SOURCE)
    target = output_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, target)

    copied_size = target.stat().st_size
    copied_hash = digest(target)
    if copied_size != size or copied_hash != expected:
        print("copy verification failed: size or sha256 mismatch",
              file=sys.stderr)
        return 1

    print(f"entry.png -> {target} ({copied_size} bytes, sha256 {copied_hash})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
