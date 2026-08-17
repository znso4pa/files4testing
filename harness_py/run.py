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
import shutil
import subprocess
import sys
import tempfile

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
    elif fmt == "iso":
        # single-file ISO: 7z streams the one member to stdout
        args = ["7z", "x", "-so", "-y", path]
    elif fmt == "zip":
        args = (["unzip", "-P", pw, "-p", path] if pw
                else ["unzip", "-p", path])
        r = subprocess.run(args, capture_output=True)
        if r.returncode != 0:
            # unzip may not support exotic zip methods or byte-volumes; 7z does
            args = (["7z", "x", "-so", "-y", f"-p{pw}", path] if pw
                    else ["7z", "x", "-so", "-y", path])
            r = subprocess.run(args, capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(f"zip extraction failed: {r.stderr[:200]!r}")
        return r.stdout
    elif fmt == "7z":
        args = (["7z", "x", "-so", "-y", f"-p{pw}", path] if pw
                else ["7z", "x", "-so", "-y", path])
    elif fmt == "rar":
        args = (["unrar", "p", "-inul", f"-p{pw}", path] if pw
                else ["unrar", "p", "-inul", path])
    elif fmt == "tar":
        args = ["tar", "-xOf", path, os.path.basename(entry["expected_file"])]
    elif fmt.startswith("tar."):
        # tar + compressor: decompress stream, then untar
        inner = fmt.split(".", 1)[1]
        tools = {"gzip": "gzip", "bzip2": "bzip2", "xz": "xz",
                 "lzma": "lzma", "lz4": "lz4", "zstd": "zstd", "brotli": "brotli"}
        if inner not in tools:
            raise ValueError(f"unsupported tar inner: {inner}")
        r = subprocess.run([tools[inner], "-dc", path], capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(f"{tools[inner]} failed: {r.stderr[:200]!r}")
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmpf:
            tmpf.write(r.stdout)
            tmp_path = tmpf.name
        try:
            r2 = subprocess.run(["tar", "-xOf", tmp_path, os.path.basename(entry["expected_file"])],
                                capture_output=True)
        finally:
            os.unlink(tmp_path)
        if r2.returncode != 0:
            raise RuntimeError(f"tar failed: {r2.stderr[:200]!r}")
        return r2.stdout
    else:
        raise ValueError(f"unsupported format: {fmt}")

    r = subprocess.run(args, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"{args[0]} failed: {r.stderr[:200]!r}")
    return r.stdout


def decompress_tree(entry: dict, input_bytes: bytes, out_dir: str) -> None:
    """Extract a multi-file / tree entry into out_dir using reference tools.

    Default reference implementation mirroring verify.sh. Implement your own
    when you support tree extraction natively.
    """
    path = os.path.join(ROOT, entry["path"])
    fmt = entry["format"]
    pw = entry.get("password")
    if fmt == "iso":
        subprocess.run(["7z", "x", "-y", f"-o{out_dir}", path],
                       capture_output=True, check=True)
    elif fmt == "tar":
        subprocess.run(["tar", "-xf", path, "-C", out_dir], check=True)
    elif fmt.startswith("tar."):
        inner = fmt.split(".", 1)[1]
        tools = {"gzip": "gzip", "bzip2": "bzip2", "xz": "xz",
                 "lzma": "lzma", "lz4": "lz4", "zstd": "zstd", "brotli": "brotli"}
        if inner not in tools:
            raise ValueError(f"unsupported tar inner: {inner}")
        r = subprocess.run([tools[inner], "-dc", path], capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(f"{tools[inner]} failed: {r.stderr[:200]!r}")
        with tempfile.NamedTemporaryFile(delete=False) as tmpf:
            tmpf.write(r.stdout)
            tmp_path = tmpf.name
        try:
            subprocess.run(["tar", "-xf", tmp_path, "-C", out_dir], check=True)
        finally:
            os.unlink(tmp_path)
    elif fmt == "zip":
        args = (["unzip", "-o", "-q", "-P", pw, path, "-d", out_dir] if pw
                else ["unzip", "-o", "-q", path, "-d", out_dir])
        subprocess.run(args, capture_output=True)
    elif fmt == "7z":
        args = (["7z", "x", "-y", f"-o{out_dir}", f"-p{pw}", path] if pw
                else ["7z", "x", "-y", f"-o{out_dir}", path])
        subprocess.run(args, capture_output=True, check=True)
    elif fmt == "rar":
        args = (["unrar", "x", "-inul", f"-p{pw}", path, out_dir + "/"] if pw
                else ["unrar", "x", "-inul", path, out_dir + "/"])
        subprocess.run(args, capture_output=True)
    else:
        raise ValueError(f"no tree extractor for format: {fmt}")


def tree_sha256(out_dir: str, expected_files) -> str:
    h = hashlib.sha256()
    for ef in sorted(expected_files, key=lambda x: x["path"]):
        h.update(ef["path"].encode())
        h.update(b"\0")
        with open(os.path.join(out_dir, ef["path"]), "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
    return h.hexdigest()


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
        if entry["format"] == "cso":
            # no reference CLI; validated at generation time (round-trip)
            print(f"[skip] {entry['path']} (cso: no reference CLI)")
            continue
        try:
            expected_files = entry.get("expected_files")
            if expected_files:
                out_dir = tempfile.mkdtemp(prefix="uu_harness_tree_")
                try:
                    decompress_tree(entry, b"", out_dir)
                    # assert every expected file's sha256
                    for ef in expected_files:
                        fp = os.path.join(out_dir, ef["path"])
                        if not os.path.isfile(fp):
                            raise RuntimeError(f"tree member missing: {ef['path']}")
                        with open(fp, "rb") as f:
                            if sha256(f.read()) != ef["sha256"]:
                                raise RuntimeError(f"tree member mismatch: {ef['path']}")
                    got_tree = tree_sha256(out_dir, expected_files)
                    if got_tree != entry.get("tree_sha256"):
                        raise RuntimeError("tree hash mismatch")
                    mark = "ok"
                finally:
                    shutil.rmtree(out_dir, ignore_errors=True)
                print(f"[{mark}] {entry['path']} ({entry['format']}/{entry['level']}) tree")
                pass_n += mark == "ok"
                fail_n += mark != "ok"
                continue
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
