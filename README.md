# files4testing — Compression Test Vectors

A collection of **copyright-free raw files**, compressed into **10 formats × 3 layers**
(normal / password / split-volume) at multiple levels, designed for people who
implement their own **decompressors / compressors** (e.g. in Rust) and need ready-made,
machine-verifiable test inputs.

[![verify](https://github.com/znso4pa/files4testing/actions/workflows/verify.yml/badge.svg)](https://github.com/znso4pa/files4testing/actions/workflows/verify.yml)

> **Warning: this repository is ~2 GB (including git history). Cloning takes a while.**
> Please make sure you have enough disk space and bandwidth.

## Why this exists

If you are implementing a decompressor from scratch, you need test files — and
you need to *know* what the correct output is. This repo provides:

- **260 compressed files** in 10 formats (`7z`, `zip`, `rar`, `gzip`, `bzip2`,
  `xz`, `lzma`, `lz4`, `zstd`, `brotli`), each with a known expected output.
- **3 layers**: plain, password-protected (password `123`), and 1 MB split volumes.
- **`manifest.json`**: a machine-readable catalog mapping every file to its
  expected output **SHA-256**, so you can assert correctness automatically.
- Raw files spanning very different compressibility: tiny text, incompressible
  JPEG, 30 MB highly-compressible text, 30 MB semi-compressible 32-bit RGBA bitmap.

## Quick start (for implementers)

1. Clone the repo (see warning above).
2. Pick any entry from `manifest.json`.
3. Feed the compressed file to **your** decompressor.
4. Assert `sha256(output) == entry["expected_sha256"]`.

Example entry from `manifest.json`:

```json
{
  "layer": "normal",
  "kind": "rawfile1",
  "path": "normal/rawfile1/rawfile1.mx9.7z",
  "format": "7z",
  "level": "mx9",
  "is_archive": true,
  "is_volume": false,
  "volume_count": null,
  "password": null,
  "expected_file": "rawfiles/rawfile1.txt",
  "expected_size": 1113,
  "expected_sha256": "da819b59140f5ee6a20e41029bd74cb8c428fb9871c2eb7d7e17e74a26d12f8a"
}
```

For volume entries (`is_volume: true`), the listed `path` is the **first
volume** (`.part01.rar` / `.7z.001`); decompress the whole set to get the output.

## Raw files

| File | Size | Characteristics |
|------|------|-----------------|
| `rawfiles/rawfile1.txt` | 1.1 KB | Text, highly compressible (Shakespeare, Romeo and Juliet excerpt) |
| `rawfiles/rawfile2.jpg` | 9.4 MB | Already-compressed image, nearly incompressible |
| `rawfiles/rawfile3.txt` | 30.8 MB | Concatenated Project Gutenberg books, highly compressible |
| `rawfiles/rawfile4.bmp` | 29.9 MB | NASA photo converted to 32-bit RGBA bitmap, semi-compressible |
| `rawfiles/combination.bin` | 69.7 MB | The four files concatenated, as a combined input |

SHA-256 of every raw file is in `REPORT.md` and `manifest.json`.

## Directory layout

```
normal/    no encryption, no volumes (all formats × multiple levels)
password/  encrypted, password is 123 (formats supporting encryption: 7z/zip/rar)
split/     1 MB split volumes (formats supporting volumes: 7z/rar)
  ├─ rawfile1/      rawfile1 compressed
  ├─ rawfile2/      rawfile2 compressed
  ├─ rawfile3/      rawfile3 compressed
  ├─ rawfile4/      rawfile4 compressed
  └─ combination/   combination.bin compressed
```

## Level strategy

| Files | Strategy |
|-------|----------|
| `rawfile1` / `rawfile2` | Full levels (every format × multiple levels) |
| `rawfile3` / `rawfile4` / `combination` | One representative level per format, to keep size manageable |

## Formats and levels

Full-level files (`rawfile1` / `rawfile2`):

| Format | Extension | Levels |
|--------|-----------|--------|
| 7z | `.7z` | mx1 / mx5 / mx9 |
| zip | `.zip` | z1 / z6 / z9 |
| rar | `.rar` | m1 / m3 / m5 |
| gzip | `.gz` | g1 / g6 / g9 |
| bzip2 | `.bz2` | b1 / b9 |
| xz | `.xz` | x1 / x6 / x9 |
| lzma | `.lzma` | l1 / l9 |
| lz4 | `.lz4` | lz4-1 / lz4-9 / lz4-12 |
| zstd | `.zst` | zst-1 / zst-19 / zst-22 |
| brotli | `.br` | br1 / br6 / br9 |

Lean files (`rawfile3` / `rawfile4` / `combination`): one level per format —
`7z-mx9`, `zip-z9`, `rar-m5`, `gzip-g9`, `bzip2-b9`, `xz-x9`, `lzma-l9`,
`lz4-lz4-9`, `zstd-zst-19`, `brotli-br9`.

## Naming convention

`<raw name>.<format>_<level>.<extension>`, e.g. `rawfile1.mx9.7z`, `combination.zst-19.zst`.

## Passwords

All files in `password/` are encrypted with the password **`123`**.
- 7z uses `-mhe=on` (header encryption).
- rar uses `-hp` (data + header encryption).

## Split volumes

`split/` uses 1 MB volumes:
- 7z: `.7z.001`, `.7z.002` ... — start extraction from `.001`
- rar: `.part01.rar`, `.part02.rar` ... — start extraction from `part01`

## Tooling

| Script | Purpose |
|--------|---------|
| `compress.sh` | Regenerate all compressed files from `rawfiles/` |
| `gen_manifest.py` | Generate `manifest.json` (test vector catalog) |
| `gen_report.sh` | Generate `REPORT.md` (sizes, ratios, SHA-256) |
| `verify.sh` | Decompress every file with reference tools and assert SHA-256 |
| `harness/` | Rust example: run your own `Decompressor` against every vector |

## Data sources & license

| File | Source | License |
|------|--------|---------|
| `rawfile1.txt` | Shakespeare, Romeo and Juliet (excerpt) | Public domain |
| `rawfile2.jpg` | See REPORT.md (copyright-free material) | Public domain |
| `rawfile3.txt` | [Project Gutenberg](https://www.gutenberg.org/) public-domain books | Public domain (redistribution subject to Project Gutenberg license/trademark terms) |
| `rawfile4.bmp` | [NASA PIA00405](https://images.nasa.gov/details/PIA00405), Moon photographed by Galileo, 1992 | Public domain |

This repository (scripts, docs, compressed outputs) is licensed under the
**MIT License** — see `LICENSE`.
Compressed outputs are lossless transforms of public-domain input and remain in
the public domain.
