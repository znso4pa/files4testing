#!/usr/bin/env python3
"""files4testing Python harness.

Run your own decompressor against every test vector:

    python3 harness_py/run.py            # full suite
    SKIP_COMBINATION=1 python3 harness_py/run.py

The harness reads manifest.json, calls `decompress(entry, input_bytes)`,
and asserts sha256(output) == entry["expected_sha256"].

Implement `decompress()` below with your own logic. The default shell-based
implementation is a working reference that proves the harness end-to-end.
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ===========================================================================
# Implement your decompressor here.
# ===========================================================================

def decompress(entry: dict, input_bytes: bytes) -> bytes:
    """Return the decompressed bytes for `entry`, or raise on failure.

    entry has keys: path, format, level, is_archive, is_volume,
    volume_count, password, expected_file, expected_size, expected_sha256.
    """
    path = os.path.join(ROOT, entry["path"])
    fmt = entry["format"]
    pw = entry.get("password")
    args = []

    if fmt in ("gzip", "bzip2", "xz", "lzma", "lz4", "zstd", "brotli"):
        args = [fmt, "-dc", path]
    elif fmt == "zip":
        args = (["unzip", "-P", pw, "-p", path] if pw
                else ["unzip", "-p", path])
    elif fmt == "7z":
        args = (["7z", "x", "-so", "-y", f"-p{pw}", path] if pw
                else ["7z", "x", "-so", "-y", path])
    elif fmt == "rar":
        args = (["unrar", "p", "-inul", f"-p{pw}", path] if pw
                else ["unrar", "p", "-inul", path])
    else:
        raise ValueError(f"unsupported format: {fmt}")

    r = subprocess.run(args, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"{args[0]} failed: {r.stderr[:200]!r}")
    return r.stdout


# ===========================================================================
# End of user implementation.
# ===========================================================================

def main():
    if not (os.path.isdir(os.path.join(ROOT, "normal"))
            and os.path.isdir(os.path.join(ROOT, "rawfiles"))):
        print("Data not found. Compressed files are hosted in the GitHub Release — "
              "download the tarballs and extract them into the repo root first. "
              "See README.md.", file=sys.stderr)
        sys.exit(2)
    with open(os.path.join(ROOT, "manifest.json")) as f:
        manifest = json.load(f)
    skip_big = os.environ.get("SKIP_COMBINATION") == "1"

    pass_n = fail_n = 0
    for entry in manifest["entries"]:
        if skip_big and entry["kind"] == "combination":
            print(f"[skip] {entry['path']}")
            continue
        try:
            out = decompress(entry, b"")
            got = sha256(out)
            ok = got == entry["expected_sha256"]
            mark = "ok" if ok else "MISMATCH"
            print(f"[{mark}] {entry['path']} ({entry['format']}/{entry['level']}) {got}")
            pass_n += ok
            fail_n += not ok
        except Exception as e:
            print(f"[error] {entry['path']}: {e}")
            fail_n += 1

    print(f"\nPASS: {pass_n}  FAIL: {fail_n}")
    sys.exit(0 if fail_n == 0 else 1)


if __name__ == "__main__":
    main()
