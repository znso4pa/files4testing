#!/usr/bin/env bash
# Verify every test vector in manifest.json using reference tools.
# For each entry: decompress -> sha256 -> compare with expected_sha256
# (or extract the tree and assert expected_files/tree_sha256).
# Usage: ./verify.sh [--fast]   (--fast skips the big combination files)
set -euo pipefail
cd "$(dirname "$0")"

FAST="${1:-}"

# Data lives in the GitHub Release. If not extracted, point the user there.
if [ ! -d normal ] || [ ! -d rawfiles ]; then
  echo "Data not found. The compressed files are hosted in the GitHub Release."
  echo "Download and extract them into this directory first, e.g.:"
  echo "  curl -L -o normal.tar.gz https://github.com/znso4pa/files4testing/releases/latest/download/normal.tar.gz"
  echo "  curl -L -o password.tar.gz https://github.com/znso4pa/files4testing/releases/latest/download/password.tar.gz"
  echo "  curl -L -o split.tar.gz https://github.com/znso4pa/files4testing/releases/latest/download/split.tar.gz"
  echo "  curl -L -o rawfiles.tar.gz https://github.com/znso4pa/files4testing/releases/latest/download/rawfiles.tar.gz"
  echo "  tar xzf normal.tar.gz && tar xzf password.tar.gz && tar xzf split.tar.gz && tar xzf rawfiles.tar.gz"
  exit 2
fi

# Produce TSV: path<TAB>format<TAB>password<TAB>expected_file<TAB>expected_sha256<TAB>tree_sha256<TAB>expected_files(json)
python3 - <<'PY' > /tmp/verify_manifest.tsv
import json
m = json.load(open("manifest.json"))
for e in m["entries"]:
    files = e.get("expected_files")
    files_json = json.dumps(files, separators=(",", ":")) if files else "-"
    print("\t".join([
        e["path"],
        e["format"],
        e["password"] or "-",
        e.get("expected_file") or "-",
        e.get("expected_sha256") or "-",
        e.get("tree_sha256") or "-",
        files_json,
    ]))
PY

PASS=0
FAIL=0
SKIP=0
declare -a FAILED=()
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

extract_to_file() {
  # args: path format password expected_file  -> writes decompressed bytes to $TMP/out
  local path="$1" fmt="$2" pw="$3" expfile="$4"
  case "$fmt" in
    gzip)  gzip -dc "$path" > "$TMP/out" ;;
    bzip2) bzip2 -dc "$path" > "$TMP/out" ;;
    xz)    xz -dc "$path" > "$TMP/out" ;;
    lzma)  lzma -dc "$path" > "$TMP/out" ;;
    lz4)   lz4 -dc "$path" > "$TMP/out" 2>/dev/null ;;
    zstd)  zstd -dc "$path" > "$TMP/out" ;;
    brotli) brotli -dc "$path" > "$TMP/out" ;;
    zip)   if [ "$pw" = "-" ]; then
             unzip -p "$path" > "$TMP/out" 2>/dev/null || 7z x -so -y "$path" > "$TMP/out"
           else
             unzip -P "$pw" -p "$path" > "$TMP/out" 2>/dev/null || 7z x -so -y -p"$pw" "$path" > "$TMP/out"
           fi ;;
    7z)    if [ "$pw" = "-" ]; then 7z x -so -y "$path" > "$TMP/out"; else 7z x -so -y -p"$pw" "$path" > "$TMP/out"; fi ;;
    rar)   if [ "$pw" = "-" ]; then unrar p -inul "$path" > "$TMP/out"; else unrar p -inul -p"$pw" "$path" > "$TMP/out"; fi ;;
    iso)   7z x -so -y "$path" > "$TMP/out" ;;
    tar)   tar -xOf "$path" "$(basename "$expfile")" > "$TMP/out" ;;
    tar.*) # tar + compressor: decompress stream first, then untar
      local tmpgz="$TMP/tarstream"
      local inner="${fmt#tar.}"
      case "$inner" in
        gzip)  gzip -dc "$path" > "$tmpgz" ;;
        bzip2) bzip2 -dc "$path" > "$tmpgz" ;;
        xz)    xz -dc "$path" > "$tmpgz" ;;
        lzma)  lzma -dc "$path" > "$tmpgz" ;;
        lz4)   lz4 -dc "$path" > "$tmpgz" 2>/dev/null ;;
        zstd)  zstd -dc "$path" > "$tmpgz" ;;
        brotli) brotli -dc "$path" > "$tmpgz" ;;
        *) echo "unknown tar inner: $inner" >&2; return 1 ;;
      esac
      tar -xOf "$tmpgz" "$(basename "$expfile")" > "$TMP/out"
      ;;
    cso)   # no reference CLI; round-trip validated at generation time
      echo "SKIP $path (no reference CLI for cso)"
      return 2
      ;;
    *) echo "unknown format: $fmt" >&2; return 1 ;;
  esac
}

extract_to_tree() {
  # args: path format password outdir  -> extracts archive tree into outdir
  local path="$1" fmt="$2" pw="$3" out="$4"
  rm -rf "$out"; mkdir -p "$out"
  case "$fmt" in
    iso)   7z x -y -o"$out" "$path" >/dev/null ;;
    tar)   tar -xf "$path" -C "$out" ;;
    tar.*) # tar + compressor: decompress stream first, then untar
      local tmpgz="$TMP/tarstream_tree"
      local inner="${fmt#tar.}"
      case "$inner" in
        gzip)  gzip -dc "$path" > "$tmpgz" ;;
        bzip2) bzip2 -dc "$path" > "$tmpgz" ;;
        xz)    xz -dc "$path" > "$tmpgz" ;;
        lzma)  lzma -dc "$path" > "$tmpgz" ;;
        lz4)   lz4 -dc "$path" > "$tmpgz" 2>/dev/null ;;
        zstd)  zstd -dc "$path" > "$tmpgz" ;;
        brotli) brotli -dc "$path" > "$tmpgz" ;;
        *) echo "unknown tar inner: $inner" >&2; return 1 ;;
      esac
      tar -xf "$tmpgz" -C "$out"
      ;;
    zip)   if [ "$pw" = "-" ]; then unzip -o -q "$path" -d "$out" 2>/dev/null; else unzip -o -q -P "$pw" "$path" -d "$out" 2>/dev/null; fi ;;
    7z)    if [ "$pw" = "-" ]; then 7z x -y -o"$out" "$path" >/dev/null; else 7z x -y -o"$out" -p"$pw" "$path" >/dev/null; fi ;;
    rar)   if [ "$pw" = "-" ]; then unrar x -inul "$path" "$out/" >/dev/null; else unrar x -inul -p"$pw" "$path" "$out/" >/dev/null; fi ;;
    *) echo "no tree extractor for $fmt" >&2; return 1 ;;
  esac
}

check_tree() {
  # args: dir files_json tree_sha  -> returns 0 if all files + tree hash match
  local dir="$1" files_json="$2" tree_sha="$3"
  python3 - "$dir" "$files_json" "$tree_sha" <<'PY'
import hashlib, json, os, sys
dirp, files_json, tree_sha = sys.argv[1], sys.argv[2], sys.argv[3]
expected = json.loads(files_json)
got = {}
for root, _, fns in os.walk(dirp):
    for fn in fns:
        fp = os.path.join(root, fn)
        rel = os.path.relpath(fp, dirp)
        h = hashlib.sha256()
        with open(fp, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        got[rel] = h.hexdigest()
for e in expected:
    if e["path"] not in got:
        print(f"  tree-file-missing {e['path']}")
        sys.exit(1)
    if got[e["path"]] != e["sha256"]:
        print(f"  tree-file-mismatch {e['path']}")
        sys.exit(1)
h = hashlib.sha256()
for e in sorted(expected, key=lambda x: x["path"]):
    h.update(e["path"].encode())
    h.update(b"\0")
    with open(os.path.join(dirp, e["path"]), "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
if h.hexdigest() != tree_sha:
    print("  tree-sha-mismatch")
    sys.exit(1)
sys.exit(0)
PY
}

while IFS=$'\t' read -r path fmt pw expfile expected tree files_json; do
  [ -n "$FAST" ] && [[ "$path" == *combination* ]] && { echo "SKIP $path (--fast)"; SKIP=$((SKIP+1)); continue; }
  if [ "$files_json" != "-" ]; then
    # multi-file / tree entry
    if ! extract_to_tree "$path" "$fmt" "$pw" "$TMP/tree"; then
      echo "ERROR $path (tree extract failed)"
      FAIL=$((FAIL+1)); FAILED+=("$path")
      continue
    fi
    if check_tree "$TMP/tree" "$files_json" "$tree"; then
      PASS=$((PASS+1))
    else
      echo "MISMATCH $path (tree)"
      FAIL=$((FAIL+1)); FAILED+=("$path")
    fi
    continue
  fi
  rc=0
  extract_to_file "$path" "$fmt" "$pw" "$expfile" || rc=$?
  if [ "$rc" = "2" ]; then
    SKIP=$((SKIP+1))
    continue
  fi
  if [ "$rc" != "0" ]; then
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
echo "PASS: $PASS  FAIL: $FAIL  SKIP: $SKIP"
if [ "$FAIL" -gt 0 ]; then
  echo "Failed:"
  printf '  %s\n' "${FAILED[@]}"
  exit 1
fi
echo "All positive test vectors verified OK."

# --- Negative cases: a correct decompressor must REJECT these --------------
NPASS=0
NFAIL=0
NFAILED=()

# expected_fail path format password  -> returns 0 if the tool FAILS as expected
expected_fail() {
  local path="$1" fmt="$2" pw="$3"
  case "$fmt" in
    gzip)   ! gzip -dc "$path" > "$TMP/out" 2>/dev/null ;;
    xz)     ! xz -dc "$path" > "$TMP/out" 2>/dev/null ;;
    7z)     if [ "$pw" = "-" ]; then ! 7z x -so -y "$path" > "$TMP/out" 2>/dev/null; else ! 7z x -so -y -p"$pw" "$path" > "$TMP/out" 2>/dev/null; fi ;;
    zip)    if [ "$pw" = "-" ]; then ! unzip -p "$path" > "$TMP/out" 2>/dev/null; else ! unzip -P "$pw" -p "$path" > "$TMP/out" 2>/dev/null; fi ;;
    rar)    if [ "$pw" = "-" ]; then ! unrar p -inul "$path" > "$TMP/out" 2>/dev/null; else ! unrar p -inul -p"$pw" "$path" > "$TMP/out" 2>/dev/null; fi ;;
    iso)    ! 7z x -so -y "$path" > "$TMP/out" 2>/dev/null ;;
    zstd)   ! zstd -dc "$path" > "$TMP/out" 2>/dev/null ;;
    lz4)    ! lz4 -dc "$path" > "$TMP/out" 2>/dev/null ;;
    lzma)   ! lzma -dc "$path" > "$TMP/out" 2>/dev/null ;;
    bzip2)  ! bzip2 -dc "$path" > "$TMP/out" 2>/dev/null ;;
    brotli) ! brotli -dc "$path" > "$TMP/out" 2>/dev/null ;;
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