#!/usr/bin/env bash
set -euo pipefail

RAW="rawfiles"
PASS="123"
VOL="1M"

# 原始文件定义：<kind> <文件名> <档位策略 full|lean>
KINDS=(
  "rawfile1 rawfile1.txt full"
  "rawfile2 rawfile2.jpg full"
  "rawfile3 rawfile3.txt lean"
  "rawfile4 rawfile4.bmp lean"
  "rawfile5 rawfile5.bin full"
  "rawfile6 rawfile6.json full"
  "rawfile7 rawfile7.c full"
  "rawfile8 rawfile8.fa full"
  "combination combination.bin lean"
)

rm -rf normal password split
mkdir -p normal password split

# 重建 combination.bin = 全部文件拼接
cat "$RAW/rawfile1.txt" "$RAW/rawfile2.jpg" "$RAW/rawfile3.txt" "$RAW/rawfile4.bmp" \
    "$RAW/rawfile5.bin" "$RAW/rawfile6.json" "$RAW/rawfile7.c" "$RAW/rawfile8.fa" \
    > "$RAW/combination.bin"

gen() {
  local layer="$1" kind="$2" fname="$3" policy="$4"
  local out="$layer/$kind"
  mkdir -p "$out"
  local src="$RAW/$fname"
  local stem="$kind"

  # --- 7z ---------------------------------------------------------------
  for lvl in 1 5 9; do
    [ "$policy" = "lean" ] && [ "$lvl" != "9" ] && continue
    local opts=(-mx$lvl -mmt=on)
    [ "$layer" = "password" ] && opts+=(-p"$PASS" -mhe=on)
    [ "$layer" = "split" ] && opts+=(-v$VOL)
    ( cd "$RAW" && 7z a -y -t7z "${opts[@]}" "../$out/$stem.mx$lvl.7z" "$fname" ) >/dev/null
  done

  # --- zip (no split support) -------------------------------------------
  if [ "$layer" != "split" ]; then
    for lvl in 1 6 9; do
      [ "$policy" = "lean" ] && [ "$lvl" != "9" ] && continue
      local zopts=(-"$lvl" -j)
      [ "$layer" = "password" ] && zopts+=(-P "$PASS")
      ( cd "$RAW" && zip "${zopts[@]}" "../$out/$stem.z$lvl.zip" "$fname" ) >/dev/null
    done
  fi

  # --- rar --------------------------------------------------------------
  for lvl in 1 3 5; do
    [ "$policy" = "lean" ] && [ "$lvl" != "5" ] && continue
    local ropts=(-m$lvl -ep1 -idq)
    [ "$layer" = "password" ] && ropts+=(-hp"$PASS")
    [ "$layer" = "split" ] && ropts+=(-v$VOL)
    rar a "${ropts[@]}" "$out/$stem.m$lvl.rar" "$src" >/dev/null
  done

  # --- stream formats: only normal layer --------------------------------
  if [ "$layer" = "normal" ]; then
    for lvl in 1 6 9; do
      [ "$policy" = "lean" ] && [ "$lvl" != "9" ] && continue
      gzip -c -$lvl "$src" > "$out/$stem.g$lvl.gz"
    done

    for lvl in 1 9; do
      [ "$policy" = "lean" ] && [ "$lvl" != "9" ] && continue
      bzip2 -c -$lvl "$src" > "$out/$stem.b$lvl.bz2"
    done

    for lvl in 1 6 9; do
      [ "$policy" = "lean" ] && [ "$lvl" != "9" ] && continue
      xz -c -$lvl "$src" > "$out/$stem.x$lvl.xz"
    done

    for lvl in 1 9; do
      [ "$policy" = "lean" ] && [ "$lvl" != "9" ] && continue
      lzma -c -$lvl "$src" > "$out/$stem.l$lvl.lzma"
    done

    for lvl in 1 6 9; do
      [ "$policy" = "lean" ] && [ "$lvl" != "9" ] && continue
      brotli -c -q $lvl "$src" > "$out/$stem.br$lvl.br"
    done

    for lvl in 1 9 12; do
      [ "$policy" = "lean" ] && [ "$lvl" != "9" ] && continue
      lz4 -$lvl -c "$src" > "$out/$stem.lz4-$lvl.lz4"
    done

    for lvl in 1 19 22; do
      [ "$policy" = "lean" ] && [ "$lvl" != "19" ] && continue
      local zopts=(-c)
      [ "$lvl" -ge 20 ] && zopts+=(--ultra)
      zstd -$lvl "${zopts[@]}" "$src" > "$out/$stem.zst-$lvl.zst" 2>/dev/null
    done

    # --- tar + tar+compressor (archive formats, normal layer only) --------
    # 纯 tar（不压缩，作为归档基线）
    tar -C "$RAW" -cf "$out/$stem.tar.tar" "$fname"

    for lvl in 1 6 9; do
      [ "$policy" = "lean" ] && [ "$lvl" != "9" ] && continue
      tar -C "$RAW" -cf - "$fname" | gzip -$lvl -c > "$out/$stem.tar.g$lvl.tar.gz"
    done

    for lvl in 1 9; do
      [ "$policy" = "lean" ] && [ "$lvl" != "9" ] && continue
      tar -C "$RAW" -cf - "$fname" | bzip2 -$lvl -c > "$out/$stem.tar.b$lvl.tar.bz2"
    done

    for lvl in 1 6 9; do
      [ "$policy" = "lean" ] && [ "$lvl" != "9" ] && continue
      tar -C "$RAW" -cf - "$fname" | xz -$lvl -c > "$out/$stem.tar.x$lvl.tar.xz"
    done

    for lvl in 1 9; do
      [ "$policy" = "lean" ] && [ "$lvl" != "9" ] && continue
      tar -C "$RAW" -cf - "$fname" | lzma -$lvl -c > "$out/$stem.tar.l$lvl.tar.lzma"
    done

    for lvl in 1 6 9; do
      [ "$policy" = "lean" ] && [ "$lvl" != "9" ] && continue
      tar -C "$RAW" -cf - "$fname" | brotli -c -q $lvl > "$out/$stem.tar.br$lvl.tar.br"
    done

    for lvl in 1 9 12; do
      [ "$policy" = "lean" ] && [ "$lvl" != "9" ] && continue
      tar -C "$RAW" -cf - "$fname" | lz4 -$lvl -c > "$out/$stem.tar.lz4-$lvl.tar.lz4"
    done

    for lvl in 1 19 22; do
      [ "$policy" = "lean" ] && [ "$lvl" != "19" ] && continue
      local zopts=(-c)
      [ "$lvl" -ge 20 ] && zopts+=(--ultra)
      tar -C "$RAW" -cf - "$fname" | zstd -$lvl "${zopts[@]}" > "$out/$stem.tar.zst-$lvl.tar.zst" 2>/dev/null
    done
  fi
}

for kind_info in "${KINDS[@]}"; do
  set -- $kind_info
  kind=$1 fname=$2 policy=$3
  gen normal "$kind" "$fname" "$policy"
  gen password "$kind" "$fname" "$policy"
  gen split "$kind" "$fname" "$policy"
done

echo "done"
