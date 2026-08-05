#!/usr/bin/env bash
# Generate negative/fault test cases: corrupted, truncated, wrong-password,
# and missing-volume inputs. These should be REJECTED by a correct decompressor
# (decompression must fail cleanly, not crash or emit wrong output).
set -euo pipefail
cd "$(dirname "$0")"

FAULTS="faults"
rm -rf "$FAULTS"
mkdir -p "$FAULTS"

copy() { cp "$1" "$FAULTS/$2"; }

# 1) truncated files (cut in half) — stream formats + archive formats
for f in \
  normal/rawfile1/rawfile1.g9.gz \
  normal/rawfile1/rawfile1.x9.xz \
  normal/rawfile1/rawfile1.mx9.7z \
  normal/rawfile1/rawfile1.m5.rar \
  normal/rawfile1/rawfile1.z9.zip; do
  base=$(basename "$f")
  sz=$(stat -f%z "$f")
  dd if="$f" of="$FAULTS/truncated-$base" bs=1 count=$((sz/2)) 2>/dev/null
done

# 2) corrupted: flip bytes in the middle
for f in \
  normal/rawfile1/rawfile1.g9.gz \
  normal/rawfile1/rawfile1.mx9.7z; do
  base=$(basename "$f")
  python3 - "$f" "$FAULTS/corrupt-$base" <<'PY'
import sys
src, dst = sys.argv[1], sys.argv[2]
data = bytearray(open(src, 'rb').read())
mid = len(data) // 2
for i in range(4):
    data[mid + i] ^= 0xFF
open(dst, 'wb').write(data)
PY
done

# 3) wrong password — copy a password-layer file but must fail with 123
for f in \
  password/rawfile1/rawfile1.mx9.7z \
  password/rawfile1/rawfile1.z9.zip \
  password/rawfile1/rawfile1.m5.rar; do
  base=$(basename "$f")
  cp "$f" "$FAULTS/wrongpass-$base"
done

# 4) missing volume — copy ONLY part01 of a split rar (needs other volumes)
cp split/rawfile2/rawfile2.m5.part01.rar "$FAULTS/missingvol-rawfile2.part01.rar"
cp split/combination/combination.m5.part01.rar "$FAULTS/missingvol-combination.part01.rar"

# 5) zero-length file
: > "$FAULTS/empty.bin"

echo "negative cases generated in $FAULTS/"
ls -la "$FAULTS/"
