#!/usr/bin/env python3
"""news-image-25: hand the grader the 25 November 2026 summary image.

The image itself is committed at assets/entry.png (drawn in this
session by draw25.py from that day's reported world news). This
entrypoint copies those exact bytes to the output path, so the two
grading runs always produce an identical file: no clock, no random
source, no network.

SPDX-License-Identifier: MIT
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "assets" / "entry.png"
NAME = "entry.png"
LIMIT = 1_048_576  # the gate's 1 MiB ceiling


def target() -> Path:
    folder = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return Path(folder) / NAME


def publish() -> int:
    data = SOURCE.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        print("asset is not a PNG", file=sys.stderr)
        return 1
    if len(data) > LIMIT:
        print(f"image too large: {len(data)} bytes", file=sys.stderr)
        return 1
    dest = target()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as handle:
        handle.write(data)
    again = dest.read_bytes()
    if again != data:
        print("copy mismatch", file=sys.stderr)
        return 1
    print(f"{NAME}: {len(data)} bytes sha256={hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(publish())
