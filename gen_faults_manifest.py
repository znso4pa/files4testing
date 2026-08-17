#!/usr/bin/env python3
"""Generate faults/manifest.json — negative test cases.

Each negative entry describes a fault file and how a correct decompressor
should REJECT it: attempting to decompress must fail (error), not succeed.
verify.sh runs these and asserts the reference tool exits non-zero.
"""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

# (filename, format, expected_reject_reason, command template hints)
# format uses the same names as manifest entries.
NEGATIVE = [
    # truncated (half) files
    ("truncated-rawfile1.g9.gz", "gzip", "truncated gzip stream"),
    ("truncated-rawfile1.x9.xz", "xz", "truncated xz stream"),
    ("truncated-rawfile1.mx9.7z", "7z", "truncated 7z archive"),
    ("truncated-rawfile1.m5.rar", "rar", "truncated rar archive"),
    ("truncated-rawfile1.z9.zip", "zip", "truncated zip archive"),
    ("truncated-rawfile1.zst-19.zst", "zstd", "truncated zstd stream"),
    ("truncated-rawfile1.lz4-9.lz4", "lz4", "truncated lz4 stream"),
    ("truncated-rawfile1.b9.bz2", "bzip2", "truncated bzip2 stream"),
    ("truncated-rawfile1.br9.br", "brotli", "truncated brotli stream"),
    ("truncated-rawfile1.l9.lzma", "lzma", "truncated lzma stream"),
    # corrupted (flipped bytes)
    ("corrupt-rawfile1.g9.gz", "gzip", "corrupted gzip stream (CRC)"),
    ("corrupt-rawfile1.mx9.7z", "7z", "corrupted 7z archive"),
    ("corrupt-rawfile1.z9.zip", "zip", "corrupted zip archive (CRC)"),
    ("corrupt-rawfile1.m5.rar", "rar", "corrupted rar archive"),
    ("corrupt-rawfile1.x9.xz", "xz", "corrupted xz stream"),
    ("corrupt-rawfile1.l9.lzma", "lzma", "corrupted lzma stream"),
    # wrong password
    ("wrongpass-rawfile1.mx9.7z", "7z", "wrong password (7z)", "999"),
    ("wrongpass-rawfile1.z9.zip", "zip", "wrong password (zip)", "999"),
    ("wrongpass-rawfile1.m5.rar", "rar", "wrong password (rar)", "999"),
    # missing volumes
    ("missingvol-rawfile2.part01.rar", "rar", "missing subsequent rar volumes", None),
    ("missingvol-combination.part01.rar", "rar", "missing subsequent rar volumes", None),
    ("missingvol-rawfile2.7z.001", "7z", "missing subsequent 7z volumes", None),
    # empty
    ("empty.bin", "gzip", "empty input", None),
]

def main():
    entries = []
    for row in NEGATIVE:
        fn, fmt, reason = row[0], row[1], row[2]
        wrong_pw = row[3] if len(row) > 3 else None
        p = os.path.join(ROOT, "faults", fn)
        if not os.path.exists(p):
            print(f"warning: {p} not found, skipping")
            continue
        entries.append({
            "path": os.path.join("faults", fn),
            "format": fmt,
            "reason": reason,
            # password to ATTEMPT (wrong on purpose for the wrongpass cases)
            "password": wrong_pw,
        })

    manifest = {
        "name": "files4testing negative test vectors",
        "description": (
            "A correct decompressor must REJECT every entry: attempting to "
            "decompress must fail cleanly (non-zero exit / error), not crash "
            "or produce output. verify.sh asserts reference tools fail."
        ),
        "entries": entries,
    }
    with open(os.path.join(ROOT, "faults", "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"faults/manifest.json: {len(entries)} negative cases")

if __name__ == "__main__":
    main()
