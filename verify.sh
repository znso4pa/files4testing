#!/usr/bin/env bash
# Verify every test vector in manifest.json using reference tools.
# For each entry: decompress -> sha256 -> compare with expected_sha256.
# Usage: ./verify.sh [--fast]   (--fast skips the big combination files)
set -euo pipefail
cd "$(dirname "$0")"

FAST="${1:-}"

# Produce TSV: path<TAB>format<TAB>password<TAB>expected_sha256
python3 - <<'PY' > /tmp/verify_manifest.tsv
import json
m = json.load(open("manifest.json"))
for e in m["entries"]:
    print("\t".join([e["path"], e["format"], e["password"] or "-", e["expected_sha256"]]))
PY

PASS=0
FAIL=0
declare -a FAILED=()
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

extract_to_file() {
  # args: path format password  -> writes decompressed bytes to $TMP/out
  local path="$1" fmt="$2" pw="$3"
  case "$fmt" in
    gzip)  gzip -dc "$path" > "$TMP/out" ;;
    bzip2) bzip2 -dc "$path" > "$TMP/out" ;;
    xz)    xz -dc "$path" > "$TMP/out" ;;
    lzma)  lzma -dc "$path" > "$TMP/out" ;;
    lz4)   lz4 -dc "$path" > "$TMP/out" 2>/dev/null ;;
    zstd)  zstd -dc "$path" > "$TMP/out" ;;
    brotli) brotli -dc "$path" > "$TMP/out" ;;
    zip)   if [ "$pw" = "-" ]; then unzip -p "$path" > "$TMP/out" 2>/dev/null; else unzip -P "$pw" -p "$path" > "$TMP/out" 2>/dev/null; fi ;;
    7z)    if [ "$pw" = "-" ]; then 7z x -so -y "$path" > "$TMP/out"; else 7z x -so -y -p"$pw" "$path" > "$TMP/out"; fi ;;
    rar)   if [ "$pw" = "-" ]; then unrar p -inul "$path" > "$TMP/out"; else unrar p -inul -p"$pw" "$path" > "$TMP/out"; fi ;;
    *) echo "unknown format: $fmt" >&2; return 1 ;;
  esac
}

while IFS=$'\t' read -r path fmt pw expected; do
  [ -n "$FAST" ] && [[ "$path" == *combination* ]] && { echo "SKIP $path (--fast)"; continue; }
  if ! extract_to_file "$path" "$fmt" "$pw"; then
    echo "ERROR $path (decompress failed)"
    FAIL=$((FAIL+1)); FAILED+=("$path")
    continue
  fi
  got=$(shasum -a 256 "$TMP/out" | awk '{print $1}')
  if [ "$got" = "$expected" ]; then
    PASS=$((PASS+1))
  else
    echo "MISMATCH $path (got $got, want $expected)"
    FAIL=$((FAIL+1)); FAILED+=("$path")
  fi
done < /tmp/verify_manifest.tsv

echo
echo "======================================"
echo "PASS: $PASS  FAIL: $FAIL"
if [ "$FAIL" -gt 0 ]; then
  echo "Failed:"
  printf '  %s\n' "${FAILED[@]}"
  exit 1
fi
echo "All positive test vectors verified OK."

# --- Negative cases: a correct decompressor must REJECT these --------------
NPASS=0
NFAIL=0
declare -a NFAILED=()

# expected_fail path format password  -> returns 0 if the tool FAILS as expected
expected_fail() {
  local path="$1" fmt="$2" pw="$3"
  case "$fmt" in
    gzip)   ! gzip -dc "$path" > "$TMP/out" 2>/dev/null ;;
    xz)     ! xz -dc "$path" > "$TMP/out" 2>/dev/null ;;
    7z)     if [ "$pw" = "-" ]; then ! 7z x -so -y "$path" > "$TMP/out" 2>/dev/null; else ! 7z x -so -y -p"$pw" "$path" > "$TMP/out" 2>/dev/null; fi ;;
    zip)    if [ "$pw" = "-" ]; then ! unzip -p "$path" > "$TMP/out" 2>/dev/null; else ! unzip -P "$pw" -p "$path" > "$TMP/out" 2>/dev/null; fi ;;
    rar)    if [ "$pw" = "-" ]; then ! unrar p -inul "$path" > "$TMP/out" 2>/dev/null; else ! unrar p -inul -p"$pw" "$path" > "$TMP/out" 2>/dev/null; fi ;;
    *) return 1 ;;
  esac
}

if [ -f faults/manifest.json ]; then
  python3 - <<'PY' > /tmp/verify_faults.tsv
import json
m = json.load(open("faults/manifest.json"))
for e in m["entries"]:
    print("\t".join([e["path"], e["format"], e["reason"], e["password"] or "-"]))
PY

  while IFS=$'\t' read -r path fmt reason pw; do
    if expected_fail "$path" "$fmt" "$pw"; then
      NPASS=$((NPASS+1))
    else
      echo "NEGATIVE-FAIL $path (decompressed successfully, should have been rejected: $reason)"
      NFAIL=$((NFAIL+1)); NFAILED+=("$path")
    fi
  done < /tmp/verify_faults.tsv
fi

echo
echo "=== Negative cases ==="
echo "NEG-PASS: $NPASS  NEG-FAIL: $NFAIL"
if [ "$NFAIL" -gt 0 ]; then
  echo "Negative cases that were NOT rejected:"
  printf '  %s\n' "${NFAILED[@]}"
  exit 1
fi
echo "All negative test vectors rejected OK."
