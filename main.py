#!/usr/bin/env python3
"""Deliver the finished news-front-page image to the grading harness.

The artwork itself is produced ahead of time by build_image.py and stored
next to this file as entry.png.  All this program has to do at run time is
place a copy of that file where the harness expects to find it: a file
called entry.png inside the directory named by the MAKEFUN_OUTPUT_DIR
environment variable, falling back to /output when the variable is unset.
Only the Python standard library is used, and no network access is needed.
"""

import filecmp
import os
import shutil
import struct
import sys

SOURCE_NAME = "entry.png"
DEFAULT_OUTPUT_DIR = "/output"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
MAX_DIMENSION = 1024


def check_image(path: str) -> str | None:
    """Return an error message if the file is not a valid in-limits PNG."""
    if os.path.getsize(path) > MAX_BYTES:
        return f"{SOURCE_NAME} exceeds the {MAX_BYTES}-byte limit"
    with open(path, "rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or not header.startswith(PNG_SIGNATURE):
        return f"{SOURCE_NAME} is not a PNG file"
    # The IHDR chunk starts at byte 8; width and height are big-endian
    # 32-bit integers at bytes 16 and 20.
    width, height = struct.unpack(">II", header[16:24])
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        return f"{SOURCE_NAME} is {width}x{height}, over {MAX_DIMENSION}px"
    return None


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    if not os.path.isfile(source):
        print(f"error: {SOURCE_NAME} not found next to main.py", file=sys.stderr)
        return 1
    problem = check_image(source)
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or DEFAULT_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    destination = os.path.join(output_dir, SOURCE_NAME)
    shutil.copyfile(source, destination)
    if not filecmp.cmp(source, destination, shallow=False):
        print("error: copied file differs from the original", file=sys.stderr)
        return 1
    print(f"wrote {destination} ({os.path.getsize(destination)} bytes, verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
