#!/usr/bin/env python3
"""Generate scan-oriented corpus for binwalk-style scanners (scan-core):

1. Small valid files of formats the scanner detects but the compression matrix
   does not cover: png, gif, tiff, pdf, elf, wav (RIFF), mpeg (MPEG-PS).
2. Embedded-at-offset archives under scan/ (valid gz/xz/lzma/zip preceded by
   N bytes of garbage) that a scanner must detect at a non-zero offset.
3. scan/manifest.json cataloging both with expected offsets.
"""
import json
import os
import struct
import zlib

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, "rawfiles")
SCAN = os.path.join(ROOT, "scan")

# --------------------------------------------------------------------------
# small valid binary files
# --------------------------------------------------------------------------

def png_1x1():
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)  # 1x1 RGB8
    raw = b"\x00\x00\x00\x00\x00"  # filter byte + 1 RGB pixel
    idat = zlib.compress(raw)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")

def gif_1x1():
    hdr = b"GIF89a"
    lsd = struct.pack("<HHBBB", 1, 1, 0x80 | 0x70, 0, 0)  # width, height, GCT flag + size
    gct = b"\xff\xff\xff\x00\x00\x00"  # 2 colors
    imd = struct.pack("<BHHHH", 0x2C, 0, 0, 1, 1) + b"\x00"
    data = b"\x02\x02\x44\x01\x00"  # LZW min code size + minimal data block
    trailer = b"\x3b"
    return hdr + lsd + gct + imd + data + trailer

def tiff_1x1():
    ifd_entries = [
        (256, 3, 1, 1),   # ImageWidth SHORT 1
        (257, 3, 1, 1),   # ImageLength SHORT 1
        (258, 3, 1, 8),   # BitsPerSample SHORT 8
        (259, 3, 1, 1),   # Compression NONE
        (262, 3, 1, 1),   # Photometric black-is-zero
        (273, 4, 1, 8),   # StripOffsets LONG -> data at offset 8+2+2+12*6+4
        (277, 3, 1, 1),   # SamplesPerPixel SHORT 1
        (278, 3, 1, 1),   # RowsPerStrip SHORT 1
        (279, 4, 1, 1),   # StripByteCounts LONG 1
    ]
    entries = b"".join(struct.pack("<HHI", t, ty, n) + struct.pack("<I", v)
                       for t, ty, n, v in ifd_entries)
    data_offset = 8 + 2 + 2 + len(entries) + 4
    entries = entries.replace(struct.pack("<I", 8), struct.pack("<I", data_offset), 1)
    body = b"II*\x00" + struct.pack("<H", len(ifd_entries)) + entries + struct.pack("<I", 0)
    body += b"\x80"  # 1 byte of image data
    return body

def pdf_min():
    return (b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\n"
            b"trailer<</Root 1 0 R>>\n%%EOF\n")

def elf64_min():
    ehdr = bytearray(64)
    ehdr[0:4] = b"\x7fELF"
    ehdr[4] = 2   # ELFCLASS64
    ehdr[5] = 1   # little-endian
    ehdr[6] = 1   # EV_CURRENT
    ehdr[7] = 0   # System V osabi
    struct.pack_into("<H", ehdr, 16, 2)    # ET_EXEC
    struct.pack_into("<H", ehdr, 18, 0x3E) # EM_X86_64
    struct.pack_into("<I", ehdr, 20, 1)    # version
    return bytes(ehdr)

def wav_min():
    fmt = struct.pack("<HHIIHH", 1, 1, 8000, 8000, 1, 8)  # PCM 8kHz mono 8-bit
    data = b"\x80"
    body = b"WAVE" + b"fmt " + struct.pack("<I", len(fmt)) + fmt
    body += b"data" + struct.pack("<I", len(data)) + data
    return b"RIFF" + struct.pack("<I", len(body)) + body

def mpeg_ps_min():
    return bytes([0, 0, 1, 0xba, 0x44, 0x00, 0x04, 0x00, 0x04, 0x01,
                  0x00, 0x00, 0x03, 0xf8, 0x00, 0x00])

# --------------------------------------------------------------------------
# embedded-at-offset archives
# --------------------------------------------------------------------------

EMBED_SOURCES = [
    ("embedded-rawfile1.g9.gz", "normal/rawfile1/rawfile1.g9.gz", "gzip"),
    ("embedded-rawfile1.x9.xz", "normal/rawfile1/rawfile1.x9.xz", "xz"),
    ("embedded-rawfile1.l9.lzma", "normal/rawfile1/rawfile1.l9.lzma", "lzma"),
    ("embedded-rawfile1.z9.zip", "normal/rawfile1/rawfile1.z9.zip", "zip"),
]
PAD = 0x1000
PAD_BYTES = (b"\x00\xff" * (PAD // 2))  # alternating garbage, distinct from magic

def main():
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(SCAN, exist_ok=True)

    scan_entries = []
    files = [
        ("rawfile_png.png", png_1x1(), "png image"),
        ("rawfile_gif.gif", gif_1x1(), "gif image"),
        ("rawfile_tiff.tiff", tiff_1x1(), "tiff image"),
        ("rawfile_pdf.pdf", pdf_min(), "pdf document"),
        ("rawfile_elf.elf", elf64_min(), "elf executable"),
        ("rawfile_wav.wav", wav_min(), "riff/wav audio"),
        ("rawfile_mpeg.mpeg", mpeg_ps_min(), "mpeg program stream"),
    ]
    for fn, data, _desc in files:
        with open(os.path.join(RAW, fn), "wb") as f:
            f.write(data)
        scan_entries.append({
            "path": os.path.join("rawfiles", fn),
            "format": fn.rsplit(".", 1)[1],
            "offset": 0,
            "kind": "raw",
        })

    for out, src, fmt in EMBED_SOURCES:
        with open(os.path.join(ROOT, src), "rb") as f:
            payload = f.read()
        with open(os.path.join(SCAN, out), "wb") as f:
            f.write(PAD_BYTES)
            f.write(payload)
        scan_entries.append({
            "path": os.path.join("scan", out),
            "format": fmt,
            "offset": len(PAD_BYTES),
            "kind": "embedded",
        })

    manifest = {
        "name": "files4testing scan corpus",
        "description": (
            "Scanner-oriented vectors: valid files of scanner-detected formats "
            "(raw kind, offset 0) and archives embedded at a non-zero offset "
            "(embedded kind). A correct scanner must report each file at the "
            "given offset and format."
        ),
        "entries": scan_entries,
    }
    with open(os.path.join(SCAN, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"scan corpus: {len(scan_entries)} entries (scan/manifest.json)")

if __name__ == "__main__":
    main()