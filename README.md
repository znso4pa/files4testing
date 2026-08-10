# files4testing — Compression Test Vectors

A collection of **copyright-free raw files**, compressed into **10 formats (+ 7 tar
variants) × 3 layers** (normal / password / split-volume) at multiple levels,
designed for people who implement their own **decompressors / compressors**
(e.g. in Rust) and need ready-made, machine-verifiable test inputs.

[![verify](https://github.com/znso4pa/files4testing/actions/workflows/verify.yml/badge.svg)](https://github.com/znso4pa/files4testing/actions/workflows/verify.yml)

> **Data files are hosted in the [GitHub Release](https://github.com/znso4pa/files4testing/releases)**
> to keep this git repo small (~MB). The git repo contains only the tooling,
> docs, and `manifest.json`.

## Getting the data

This git repository is intentionally lightweight — the actual compressed
test files (~1.3 GB) live in the [latest release](https://github.com/znso4pa/files4testing/releases).

Download the four tarballs and extract them into the repo root:

```sh
# from the repo root
curl -L -o normal.tar.gz    https://github.com/znso4pa/files4testing/releases/latest/download/normal.tar.gz
curl -L -o password.tar.gz  https://github.com/znso4pa/files4testing/releases/latest/download/password.tar.gz
curl -L -o split.tar.gz     https://github.com/znso4pa/files4testing/releases/latest/download/split.tar.gz
curl -L -o rawfiles.tar.gz  https://github.com/znso4pa/files4testing/releases/latest/download/rawfiles.tar.gz

tar xzf normal.tar.gz
tar xzf password.tar.gz
tar xzf split.tar.gz
tar xzf rawfiles.tar.gz
```

After extraction the working tree matches a full checkout, and
`./verify.sh`, the Rust/Python/Go harnesses, and `manifest.json` all work as
documented below.

## Why this exists

If you are implementing a decompressor from scratch, you need test files — and
you need to *know* what the correct output is. This repo provides:

- **587 compressed files** in 10 formats plus **7 tar variants** (`7z`, `zip`,
  `rar`, `gzip`, `bzip2`, `xz`, `lzma`, `lz4`, `zstd`, `brotli`, plus
  `tar`, `tar.gz`, `tar.bz2`, `tar.xz`, `tar.lzma`, `tar.lz4`, `tar.zst`,
  `tar.br`), each with a known expected output.
  (423 test vectors in `manifest.json` + 13 negative cases in `faults/`.)
- **3 layers**: plain, password-protected (password `123`), and 1 MB split volumes.
- **`manifest.json`**: a machine-readable catalog mapping every file to its
  expected output **SHA-256**, so you can assert correctness automatically.
- Raw files spanning very different compressibility: tiny text, incompressible
  JPEG, 30 MB highly-compressible text, 30 MB semi-compressible 32-bit RGBA
  bitmap, random data, JSON, source code, and DNA (FASTA).
- **Negative cases** in `faults/` (corrupted / truncated / wrong-password /
  missing-volume) to verify your decompressor rejects bad input cleanly.
- Reference harnesses in **Rust**, **Python**, and **Go**.

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
| `rawfiles/rawfile5.bin` | 1.5 MB | True random data (urandom), incompressible |
| `rawfiles/rawfile6.json` | 1.9 MB | Structured JSON records, moderate compressibility |
| `rawfiles/rawfile7.c` | 1.4 MB | Synthetic C source code, moderate compressibility |
| `rawfiles/rawfile8.fa` | 1.4 MB | DNA sequences (FASTA), highly compressible |
| `rawfiles/combination.bin` | ~76 MB | All files concatenated, as a combined input |

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
  ├─ rawfile5/      rawfile5 compressed
  ├─ rawfile6/      rawfile6 compressed
  ├─ rawfile7/      rawfile7 compressed
  ├─ rawfile8/      rawfile8 compressed
  └─ combination/   combination.bin compressed
faults/    negative cases (corrupted / truncated / wrong-password / missing-volume)
```

## Level strategy

| Files | Strategy |
|-------|----------|
| `rawfile1` / `rawfile2` / `rawfile5`–`rawfile8` | Full levels (every format × multiple levels) |
| `rawfile3` / `rawfile4` / `combination` | One representative level per format, to keep size manageable |

## Formats and levels

Full-level files (`rawfile1` / `rawfile2` / `rawfile5`–`rawfile8`):

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

Tar variants (normal layer only, archive of a single raw file):

| Format | Extension | Levels |
|--------|-----------|--------|
| tar (plain) | `.tar.tar` | — |
| tar + gzip | `.tar.<lvl>.tar.gz` | g1 / g6 / g9 |
| tar + bzip2 | `.tar.<lvl>.tar.bz2` | b1 / b9 |
| tar + xz | `.tar.<lvl>.tar.xz` | x1 / x6 / x9 |
| tar + lzma | `.tar.<lvl>.tar.lzma` | l1 / l9 |
| tar + lz4 | `.tar.<lvl>.tar.lz4` | lz4-1 / lz4-9 / lz4-12 |
| tar + zstd | `.tar.<lvl>.tar.zst` | zst-1 / zst-19 / zst-22 |
| tar + brotli | `.tar.<lvl>.tar.br` | br1 / br6 / br9 |

Lean files (`rawfile3` / `rawfile4` / `combination`): one level per format —
`7z-mx9`, `zip-z9`, `rar-m5`, `gzip-g9`, `bzip2-b9`, `xz-x9`, `lzma-l9`,
`lz4-lz4-9`, `zstd-zst-19`, `brotli-br9`, and `tar` + the max level of each
compressor (`tar.g9.tar.gz`, `tar.b9.tar.bz2`, `tar.x9.tar.xz`,
`tar.l9.tar.lzma`, `tar.lz4-9.tar.lz4`, `tar.zst-19.tar.zst`, `tar.br9.tar.br`).

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

## Negative cases (`faults/`)

A correct decompressor must **reject** every file in `faults/` (fail cleanly,
not crash, not emit output):

| Category | Files |
|----------|-------|
| Truncated | half of a `.gz` / `.xz` / `.7z` / `.rar` / `.zip` |
| Corrupted | flipped bytes mid-file (`.gz` / `.7z`) |
| Wrong password | `password/` archives opened with an incorrect password |
| Missing volumes | only `part01` of a split `.rar` present |
| Empty | zero-length input |

`verify.sh` asserts reference tools reject all of them
(`faults/manifest.json` lists the expected failures).

## Tooling

| Script | Purpose |
|--------|---------|
| `compress.sh` | Regenerate all compressed files from `rawfiles/` |
| `gen_manifest.py` | Generate `manifest.json` (test vector catalog) |
| `gen_report.sh` | Generate `REPORT.md` (sizes, ratios, SHA-256) |
| `verify.sh` | Decompress every file with reference tools and assert SHA-256 (incl. negative cases) |
| `gen_faults.sh` / `gen_faults_manifest.py` | Generate negative cases and `faults/manifest.json` |
| `harness/` | Rust example: run your own `Decompressor` against every vector |
| `harness_py/run.py` | Python example harness |
| `harness_go/` | Go example harness |

## Data sources & license

| File | Source | License |
|------|--------|---------|
| `rawfile1.txt` | Shakespeare, Romeo and Juliet (excerpt) | Public domain |
| `rawfile2.jpg` | See REPORT.md (copyright-free material) | Public domain |
| `rawfile3.txt` | [Project Gutenberg](https://www.gutenberg.org/) public-domain books | Public domain (redistribution subject to Project Gutenberg license/trademark terms) |
| `rawfile4.bmp` | [NASA PIA00405](https://images.nasa.gov/details/PIA00405), Moon photographed by Galileo, 1992 | Public domain |
| `rawfile5.bin` | Generated with `/dev/urandom` | Generated (no copyright) |
| `rawfile6.json` | Synthetic structured records | Generated (no copyright) |
| `rawfile7.c` | Synthetic C source | Generated (no copyright) |
| `rawfile8.fa` | Synthetic DNA (FASTA) | Generated (no copyright) |

This repository (scripts, docs, compressed outputs) is licensed under the
**MIT License** — see `LICENSE`.
Compressed outputs are lossless transforms of public-domain input and remain in
the public domain.
