#!/usr/bin/env python3
"""news-image-20261126 entry: copy the pre-rendered front page to output.

Pure standard library. The image is rendered by render.py (PIL, build
time only); this program just copies the bundled entry.png to
/output/entry.png, deterministically.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    src_size = os.path.getsize(SRC)
    dst_size = os.path.getsize(dst)
    if src_size != dst_size:
        print("size mismatch: %d != %d" % (src_size, dst_size),
              file=sys.stderr)
        return 1
    print("wrote %s (%d bytes)" % (dst, dst_size))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
