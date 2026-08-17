#!/usr/bin/env bash
# Generate the files4testing v1.2 additions:
#   - ISO 9660 vectors (single-file + tree) via hdiutil
#   - CSO vectors + multi-file tar + derived streams via gen_corpus (Rust)
#   - CLI-driven method/feature variants (7z methods, zip methods + AES,
#     zstd frames, xz filters, lz4 frames, lzma known-size, split zip,
#     rar solid/non-solid/store)
#
# Prerequisite: ./compress.sh has already produced the base vectors.
# After this, run: python3 gen_manifest.py && ./verify.sh
set -euo pipefail
cd "$(dirname "$0")"
RAW=rawfiles
GEN=gen_corpus/target/release/gen_corpus

# rawfile kind -> raw filename for single-file ISO/CSO
KIND_FILE=(rawfile1:rawfile1.txt rawfile2:rawfile2.jpg rawfile5:rawfile5.bin rawfile6:rawfile6.json)

mk_iso() { # src_dir out_iso
  rm -f "$2"
  hdiutil makehybrid -iso -joliet -o "$2" "$1" >/dev/null 2>&1
}

echo "== ISO 9660 =="
for kf in "${KIND_FILE[@]}"; do
  kind=${kf%%:*}; fn=${kf##*:}
  d="normal/$kind"; mkdir -p "$d"
  st=$(mktemp -d)
  cp "$RAW/$fn" "$st/"
  mk_iso "$st" "$d/$kind.iso"
  rm -rf "$st"
  echo "  $d/$kind.iso ($(stat -f%z "$d/$kind.iso") bytes)"
done

d="normal/rawfile_tree"; mkdir -p "$d"
st=$(mktemp -d)
mkdir -p "$st/data/sub"
cp "$RAW/rawfile1.txt" "$st/rawfile1.txt"
cp "$RAW/rawfile2.jpg" "$st/data/rawfile2.jpg"
cp "$RAW/rawfile6.json" "$st/data/rawfile6.json"
cp "$RAW/rawfile7.c" "$st/data/sub/rawfile7.c"
mk_iso "$st" "$d/rawfile_tree.iso"
rm -rf "$st"
echo "  $d/rawfile_tree.iso ($(stat -f%z "$d/rawfile_tree.iso") bytes)"

echo "== 7z methods =="
( cd "$RAW" && 7z a -y -t7z -mm=LZMA "../normal/rawfile1/rawfile1.mlzma.7z" "rawfile1.txt" ) >/dev/null
( cd "$RAW" && 7z a -y -t7z -mm=PPMd "../normal/rawfile1/rawfile1.mppmd.7z" "rawfile1.txt" ) >/dev/null
( cd "$RAW" && 7z a -y -t7z -mm=BZip2 "../normal/rawfile1/rawfile1.mbz2.7z" "rawfile1.txt" ) >/dev/null
( cd "$RAW" && 7z a -y -t7z -mm=Copy "../normal/rawfile1/rawfile1.mcopy.7z" "rawfile1.txt" ) >/dev/null
( cd "$RAW" && 7z a -y -t7z -m0=BCJ -m1=LZMA2 "../normal/rawfile1/rawfile1.mbcj.7z" "rawfile1.txt" ) >/dev/null
echo "  rawfile1.mlzma/mppmd/mbz2/mcopy/mbcj.7z"

echo "== zip methods + AES =="
( cd "$RAW" && zip -0 -j "../normal/rawfile1/rawfile1.z0.zip" "rawfile1.txt" ) >/dev/null
( cd "$RAW" && 7z a -y -tzip -mm=BZip2 "../normal/rawfile1/rawfile1.zbz2.zip" "rawfile1.txt" ) >/dev/null
( cd "$RAW" && 7z a -y -tzip -mm=LZMA "../normal/rawfile1/rawfile1.zlzma.zip" "rawfile1.txt" ) >/dev/null
mkdir -p "password/rawfile1"
( cd "$RAW" && 7z a -y -tzip -mem=AES256 -p123 "../password/rawfile1/rawfile1.zaes.zip" "rawfile1.txt" ) >/dev/null
echo "  z0/zbz2/zlzma (normal), zaes AES-256 (password)"

echo "== zstd frame variants =="
zstd --no-check -c "$RAW/rawfile1.txt" > "normal/rawfile1/rawfile1.zst-nocheck.zst" 2>/dev/null
cat "$RAW/rawfile1.txt" | zstd -c > "normal/rawfile1/rawfile1.zst-nofcs.zst" 2>/dev/null
echo "  zst-nocheck / zst-nofcs"

echo "== xz filters =="
xz --check=sha256 -c "$RAW/rawfile1.txt" > "normal/rawfile1/rawfile1.xz-sha256.xz"
xz --block-size=64K -c "$RAW/rawfile1.txt" > "normal/rawfile1/rawfile1.xz-block.xz"
python3 - "normal/rawfile1/rawfile1.xz-delta.xz" "$RAW/rawfile1.txt" <<'PY'
import lzma, sys
out, src = sys.argv[1], sys.argv[2]
d = open(src, "rb").read()
c = lzma.LZMACompressor(format=lzma.FORMAT_XZ,
                        filters=[{"id": lzma.FILTER_DELTA, "dist": 4},
                                 {"id": lzma.FILTER_LZMA2}])
open(out, "wb").write(c.compress(d) + c.flush())
PY
python3 - "normal/rawfile1/rawfile1.xz-x86.xz" "$RAW/rawfile1.txt" <<'PY'
import lzma, sys
out, src = sys.argv[1], sys.argv[2]
d = open(src, "rb").read()
c = lzma.LZMACompressor(format=lzma.FORMAT_XZ,
                        filters=[{"id": lzma.FILTER_X86},
                                 {"id": lzma.FILTER_LZMA2}])
open(out, "wb").write(c.compress(d) + c.flush())
PY
echo "  xz-sha256 / xz-block / xz-delta / xz-x86"

echo "== lz4 frames =="
lz4 --content-size -c "$RAW/rawfile1.txt" > "normal/rawfile1/rawfile1.lz4-cs.lz4"
lz4 -l -c "$RAW/rawfile1.txt" > "normal/rawfile1/rawfile1.lz4-legacy.lz4"
echo "  lz4-cs (content size) / lz4-legacy"

echo "== lzma known-size header =="
python3 - "normal/rawfile1/rawfile1.l9.size.lzma" "normal/rawfile1/rawfile1.l9.lzma" <<'PY'
import sys
out, src = sys.argv[1], sys.argv[2]
d = bytearray(open(src, "rb").read())
# lzma_alone header: props(1) dict(4) uncompressed_size(8, LE) — patch the
# size field (bytes 5..12) to the real 1113-byte output so the header
# declares a known size.
d[5:13] = (1113).to_bytes(8, "little")
open(out, "wb").write(d)
PY
lzma -dc "normal/rawfile1/rawfile1.l9.size.lzma" > /tmp/uu_lzma_size_check 2>/dev/null
if ! cmp -s /tmp/uu_lzma_size_check "$RAW/rawfile1.txt"; then
  echo "ERROR: lzma known-size vector does not decode to rawfile1" >&2; exit 1
fi
rm -f /tmp/uu_lzma_size_check
echo "  lzma l9.size (declared size)"

echo "== split zip (7-Zip byte volumes) =="
rm -f split/rawfile2/rawfile2.zsplit.zip.0*
( cd "$RAW" && 7z a -y -tzip -v1M "../split/rawfile2/rawfile2.zsplit.zip" "rawfile2.jpg" ) >/dev/null
echo "  split/rawfile2/rawfile2.zsplit.zip.001.."

echo "== rar solid / non-solid / store =="
rar a -m0 -ep1 -idq "normal/rawfile1/rawfile1.m0.rar" "$RAW/rawfile1.txt" >/dev/null
rar a -s -m3 -ep1 -idq "normal/rawfile1/rawfile1.ms.rar" "$RAW/rawfile1.txt" >/dev/null
echo "  rawfile1.m0 (store) / rawfile1.ms (solid); non-solid = default"

echo "== gen_corpus (CSO / tar tree / derived streams / spec) =="
if [ ! -x "$GEN" ]; then
  cargo build --release --manifest-path gen_corpus/Cargo.toml
fi
"$GEN"

echo "done"