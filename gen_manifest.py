#!/usr/bin/env python3
"""生成 machine-readable 测试清单 manifest.json

每个条目描述一个压缩文件（或分卷组）应解压出的内容与预期 SHA-256，
供实现者编写自己的解压器测试：decompress(path) -> bytes, 然后断言
sha256(bytes) == entry["expected_sha256"]。

v1.2.0 schema 扩展：
- 新增可选字段 `expected_files`（[{path,size,sha256}]，多文件/目录树输出）
  与 `tree_sha256`（对 sorted(path + "\\0" + bytes) 拼接做 sha256）。
  二者存在时，单文件 `expected_file/expected_sha256` 不适用。
- 流式多成员（如 gzip 双成员拼接）允许 `expected_file: null`，
  只用 `expected_sha256/expected_size`（输出 = 各成员拼接）。
- 新增 `corpus_spec.json`（见文档）：描述无法由文件命名推导的条目
  （cso→iso、树状 iso、多成员流、多文件 tar 等）。
- 修复：split 层的 7z/zip 分卷（`.7z.001` / `.zip.001`）此前未进 manifest。
"""
import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SPEC_PATH = os.path.join(ROOT, "corpus_spec.json")

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
ARCHIVE_FORMATS = {"7z", "zip", "rar", "tar", "iso"}

FORMAT_OF = {
    "7z": "7z", "zip": "zip", "rar": "rar", "tar": "tar", "iso": "iso",
    "cso": "cso",
    "gz": "gzip", "bz2": "bzip2", "xz": "xz",
    "lzma": "lzma", "lz4": "lz4", "zst": "zstd", "br": "brotli",
}

# 分卷文件识别
RAR_VOL_RE = re.compile(r"^(.+)\.part\d+\.rar$")
NUM_VOL_RE = re.compile(r"^(.+)\.(7z|zip)\.\d{3}$")
GENERIC_RE = re.compile(r"^(.+)\.([^.]*)\.([a-z0-9]{2,4})$")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_filename(fn):
    """从文件名解析 (kind, format, level, is_archive, is_volume, volume_base)。

    无法识别返回 None。volume_base 用于统计同一卷组的卷数。
    """
    # RAR 分卷: rawfile2.m1.part01.rar
    m = RAR_VOL_RE.match(fn)
    if m:
        stem = m.group(1)
        parts = stem.split(".")
        base = stem  # 卷组前缀
        return parts[0], "rar", ".".join(parts[1:]) or None, True, True, base
    # 7z/zip 数字分卷: rawfile2.mx1.7z.001
    m = NUM_VOL_RE.match(fn)
    if m:
        stem, ext = m.groups()
        fmt = FORMAT_OF.get(ext)
        if fmt is None:
            return None
        parts = stem.split(".")
        return parts[0], fmt, ".".join(parts[1:]) or None, fmt in ARCHIVE_FORMATS, True, stem
    parts = fn.split(".")
    # tar 纯归档: [kind, "tar", "tar"]
    if len(parts) == 3 and parts[1] == "tar" and parts[2] == "tar":
        return parts[0], "tar", "tar", True, False, None
    # tar 变体: [kind, "tar", lvl, "tar", ext]
    if len(parts) == 5 and parts[1] == "tar" and parts[3] == "tar":
        inner = FORMAT_OF.get(parts[4])
        if inner is None:
            return None
        return parts[0], "tar." + inner, parts[2], True, False, None
    # 单点名: <kind>.<ext>  (rawfile2.iso) — 无 level 标签
    m = re.match(r"^([^.]{1,64})\.([a-z0-9]{2,4})$", fn)
    if m:
        name, ext = m.groups()
        fmt = FORMAT_OF.get(ext)
        if fmt is None:
            return None
        return name, fmt, ext, fmt in ARCHIVE_FORMATS, False, None
    # 通用: <kind>.<tag>.<ext>  (rawfile1.g9.gz / rawfile1.mx9.7z / rawfile1.iso)
    m = GENERIC_RE.match(fn)
    if m:
        stem, tag, ext = m.groups()
        fmt = FORMAT_OF.get(ext)
        if fmt is None:
            return None
        kind = stem.split(".")[0]
        return kind, fmt, tag, fmt in ARCHIVE_FORMATS, False, None
    return None


def volume_count(base, files):
    """统计以 base 为前缀的卷文件数量"""
    if base is None:
        return None
    n = sum(1 for f in files if f == base or f.startswith(base + "."))
    return n if n > 0 else None


def tree_sha256(files):
    """对 sorted(path + '\\0' + bytes) 拼接做 sha256"""
    h = hashlib.sha256()
    for item in sorted(files, key=lambda x: x["path"]):
        h.update(item["path"].encode("utf-8"))
        h.update(b"\0")
        h.update(item["bytes"])
    return h.hexdigest()


def main():
    hashes = {k: sha256_file(os.path.join(ROOT, v)) for k, v in RAW_FILES.items()}
    sizes = {k: os.path.getsize(os.path.join(ROOT, v)) for k, v in RAW_FILES.items()}
    raw_bytes = {k: open(os.path.join(ROOT, v), "rb").read()
                 for k, v in RAW_FILES.items()}

    # 读取 corpus_spec.json（可选）
    spec_entries = []
    if os.path.isfile(SPEC_PATH):
        with open(SPEC_PATH) as f:
            spec = json.load(f)
        spec_entries = spec.get("entries", [])
    spec_paths = {e["path"] for e in spec_entries}

    entries = []
    seen = set()
    seen_groups = set()
    for layer in ("normal", "password", "split"):
        for kind, raw in RAW_FILES.items():
            d = os.path.join(ROOT, layer, kind)
            if not os.path.isdir(d):
                continue
            files = sorted(os.listdir(d))
            for fn in files:
                p = os.path.join(d, fn)
                if not os.path.isfile(p):
                    continue
                rel = os.path.relpath(p, ROOT)
                parsed = parse_filename(fn)
                if parsed is None:
                    continue
                pk, fmt, level, is_archive, is_vol, base = parsed
                if pk != kind:
                    continue
                if fmt == "cso":
                    # cso 由 corpus_spec.json 描述（输出是 iso 字节，非原始文件）
                    continue
                if rel in spec_paths:
                    continue
                if is_vol and base is not None:
                    # 同卷组只处理排序后第一个（即首卷），其余跳过
                    gkey = (layer, kind, base)
                    if gkey in seen_groups:
                        continue
                    seen_groups.add(gkey)
                if rel in seen:
                    continue
                seen.add(rel)
                vol_count = (volume_count(base, files) if is_vol else 1) if layer == "split" else None
                entries.append({
                    "layer": layer,
                    "kind": kind,
                    "path": rel,
                    "format": fmt,
                    "level": level,
                    "is_archive": is_archive,
                    "is_volume": layer == "split" and is_vol,
                    "volume_count": vol_count,
                    "password": "123" if layer == "password" else None,
                    "expected_file": raw,
                    "expected_size": sizes[kind],
                    "expected_sha256": hashes[kind],
                })

    # corpus_spec.json 条目
    for e in spec_entries:
        path = e["path"]
        if path in seen:
            continue
        seen.add(path)
        layer = e.get("layer", "normal")
        kind = e.get("kind", "")
        fmt = e.get("format", "")
        level = e.get("level", "")
        files_spec = e.get("files")
        if files_spec is not None:
            # 树状条目：解析每个成员的真实大小/SHA，计算 tree_sha256
            resolved = []
            total = 0
            for m in files_spec:
                rp = os.path.join(ROOT, m["raw"])
                data = open(rp, "rb").read()
                resolved.append({
                    "path": m["path"],
                    "size": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                })
                total += len(data)
            entries.append({
                "layer": layer,
                "kind": kind,
                "path": path,
                "format": fmt,
                "level": level,
                "is_archive": True,
                "is_volume": False,
                "volume_count": None,
                "password": e.get("password"),
                "expected_file": None,
                "expected_size": total,
                "expected_sha256": None,
                "expected_files": resolved,
                "tree_sha256": tree_sha256([{
                    "path": m["path"],
                    "bytes": open(os.path.join(ROOT, m["raw"]), "rb").read(),
                } for m in files_spec]),
                "note": e.get("note"),
            })
        else:
            # 单文件或纯流式条目
            exp_file = e.get("expected_file")
            exp_sha = e.get("expected_sha256")
            exp_size = e.get("expected_size")
            if exp_file is not None and exp_sha is None:
                exp_sha = sha256_file(os.path.join(ROOT, exp_file))
            if exp_file is not None and exp_size is None:
                exp_size = os.path.getsize(os.path.join(ROOT, exp_file))
            entries.append({
                "layer": layer,
                "kind": kind,
                "path": path,
                "format": fmt,
                "level": level,
                "is_archive": bool(e.get("is_archive", False)),
                "is_volume": False,
                "volume_count": None,
                "password": e.get("password"),
                "expected_file": exp_file,
                "expected_size": exp_size,
                "expected_sha256": exp_sha,
                "note": e.get("note"),
            })

    entries.sort(key=lambda x: (x["layer"], x["path"]))

    manifest = {
        "name": "files4testing compression test vectors",
        "version": "1.2.0",
        "description": (
            "Decompress each entry's path and assert sha256(output bytes) == "
            "expected_sha256. Archive formats (7z/zip/rar/tar/iso and tar+compressor "
            "variants) contain files named like the raw file; stream formats "
            "decompress to the raw byte stream directly. Entries with "
            "`expected_files`/`tree_sha256` produce a multi-file tree: extract all "
            "members and assert each file's sha256 plus the whole-tree hash "
            "(tree_sha256 = sha256 over sorted `path\\0+bytes` concatenation). "
            "cso entries decompress to an ISO byte stream (see expected_file, the "
            "matching .iso)."
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