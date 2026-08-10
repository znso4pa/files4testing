#!/usr/bin/env python3
"""生成 machine-readable 测试清单 manifest.json

每个条目描述一个压缩文件（或分卷组）应解压出的内容与预期 SHA-256，
供实现者编写自己的解压器测试：decompress(path) -> bytes, 然后断言
sha256(bytes) == entry["expected_sha256"]。
"""
import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

# kind -> 原始文件
RAW_FILES = {
    "rawfile1": "rawfiles/rawfile1.txt",
    "rawfile2": "rawfiles/rawfile2.jpg",
    "rawfile3": "rawfiles/rawfile3.txt",
    "rawfile4": "rawfiles/rawfile4.bmp",
    "rawfile5": "rawfiles/rawfile5.bin",
    "rawfile6": "rawfiles/rawfile6.json",
    "rawfile7": "rawfiles/rawfile7.c",
    "rawfile8": "rawfiles/rawfile8.fa",
    "combination": "rawfiles/combination.bin",
}

# 归档容器格式（解压出文件）vs 流式格式（解压出字节流）
ARCHIVE_FORMATS = {"7z", "zip", "rar", "tar"}

FORMAT_OF = {
    "7z": "7z", "zip": "zip", "rar": "rar", "tar": "tar",
    "gz": "gzip", "bz2": "bzip2", "xz": "xz",
    "lzma": "lzma", "lz4": "lz4", "zst": "zstd", "br": "brotli",
}

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def split_first_volume(path):
    """分卷文件返回首卷路径，否则返回原路径"""
    if re.search(r"\.part\d+\.rar$", path):
        return re.sub(r"\.part\d+\.rar$", ".part01.rar", path)
    if re.search(r"\.7z\.\d{3}$", path):
        return re.sub(r"\.7z\.\d{3}$", ".7z.001", path)
    return path

def main():
    hashes = {k: sha256_file(os.path.join(ROOT, v)) for k, v in RAW_FILES.items()}
    sizes = {k: os.path.getsize(os.path.join(ROOT, v)) for k, v in RAW_FILES.items()}

    entries = []
    for layer in ("normal", "password", "split"):
        for kind, raw in RAW_FILES.items():
            d = os.path.join(ROOT, layer, kind)
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                p = os.path.join(d, fn)
                if not os.path.isfile(p):
                    continue
                # 跳过非首卷的分卷文件
                canonical = split_first_volume(p)
                if canonical != p:
                    continue
                rel = os.path.relpath(canonical, ROOT)
                # 解析格式与等级
                parts = fn.split(".")
                # tar 纯归档: [kind, "tar", "tar"]
                if len(parts) == 3 and parts[1] == "tar" and parts[2] == "tar":
                    if parts[0] != kind:
                        continue
                    fmt, level, is_archive = "tar", "tar", True
                # tar 变体: [kind, "tar", lvl, "tar", ext]
                elif len(parts) == 5 and parts[1] == "tar" and parts[3] == "tar":
                    if parts[0] != kind:
                        continue
                    inner = FORMAT_OF.get(parts[4])
                    if inner is None:
                        continue
                    fmt = "tar." + inner
                    level = parts[2]
                    is_archive = True
                else:
                    m = re.match(r"^(.+)\.([^.]*)\.([a-z0-9]{2,4})$", fn)
                    if not m:
                        continue
                    stem, tag, ext = m.groups()
                    fmt = FORMAT_OF.get(ext)
                    if fmt is None:
                        continue
                    level = tag
                    is_archive = fmt in ARCHIVE_FORMATS
                vol_count = None
                if layer == "split":
                    if re.search(r"\.part\d+\.rar$", fn):
                        base = re.sub(r"\.part\d+\.rar$", "", fn)
                    else:
                        base = re.sub(r"\.\d{3}$", "", fn)
                    vol_count = sum(1 for x in os.listdir(d)
                                    if x.startswith(base))
                entries.append({
                    "layer": layer,
                    "kind": kind,
                    "path": rel,
                    "format": fmt,
                    "level": level,
                    "is_archive": is_archive,
                    "is_volume": layer == "split",
                    "volume_count": vol_count,
                    "password": "123" if layer == "password" else None,
                    "expected_file": raw,
                    "expected_size": sizes[kind],
                    "expected_sha256": hashes[kind],
                })

    manifest = {
        "name": "files4testing compression test vectors",
        "description": (
            "Decompress each entry's path and assert sha256(output bytes) == "
            "expected_sha256. Archive formats (7z/zip/rar/tar and tar+compressor "
            "variants) contain exactly one file named like the raw file; stream "
            "formats decompress to the raw byte stream directly."
        ),
        "raw_files": {k: {"path": v, "size": sizes[k], "sha256": hashes[k]}
                      for k, v in RAW_FILES.items()},
        "entries": entries,
    }

    out = os.path.join(ROOT, "manifest.json")
    with open(out, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"manifest.json 已生成: {len(entries)} 条")

if __name__ == "__main__":
    main()
