#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

sha() { shasum -a 256 "$1" | awk '{print $1}'; }

# kind -> 原始文件名
KINDS=(
  "rawfile1 rawfile1.txt"
  "rawfile2 rawfile2.jpg"
  "rawfile3 rawfile3.txt"
  "rawfile4 rawfile4.bmp"
  "combination combination.bin"
)

size_of() { stat -f%z "rawfiles/$1"; }

cat > REPORT.md <<'EOF'
# 压缩对比报告

## 原始文件

| 文件 | 大小 (字节) | SHA-256 |
|------|------------|---------|
EOF

for pair in "${KINDS[@]}"; do
  set -- $pair
  echo "| $1 | $(size_of "$2") | $(sha "rawfiles/$2") |" >> REPORT.md
done

cat >> REPORT.md <<'EOF'

## 说明
- `rawfile1.txt`（1.1 KB）：文本，高度可压缩（莎士比亚《罗密欧与朱丽叶》节选）
- `rawfile2.jpg`（9.4 MB）：已压缩图片，近乎不可压
- `rawfile3.txt`（30.8 MB）：Gutenberg 公版英文书拼接，高度可压缩
- `rawfile4.bmp`（29.9 MB）：NASA 公版月球照片转 32 位 RGBA 位图，半可压
- `combination.bin`（69.7 MB）：以上四个文件直接拼接，作为组合测试输入

档位策略：
- `rawfile1` / `rawfile2`：全档位（多等级）
- `rawfile3` / `rawfile4` / `combination`：精简档位（每格式一个代表等级），控制体积

## normal / 压缩率

| 文件 | 原始大小 | 压缩后 | 压缩率 |
|------|---------|--------|--------|
EOF

for pair in "${KINDS[@]}"; do
  set -- $pair
  kind=$1
  orig=$(size_of "$2")
  for f in $(find "normal/$kind" -type f | sort); do
    sz=$(stat -f%z "$f")
    ratio=$(awk -v o="$orig" -v c="$sz" 'BEGIN{printf "%.2f%%", c/o*100}')
    echo "| $f | $orig | $sz | $ratio |" >> REPORT.md
  done
done

cat >> REPORT.md <<'EOF'

## password（密码：`123`）/ 压缩率

| 文件 | 原始大小 | 压缩后 | 压缩率 |
|------|---------|--------|--------|
EOF

for pair in "${KINDS[@]}"; do
  set -- $pair
  kind=$1
  orig=$(size_of "$2")
  for f in $(find "password/$kind" -type f | sort); do
    sz=$(stat -f%z "$f")
    ratio=$(awk -v o="$orig" -v c="$sz" 'BEGIN{printf "%.2f%%", c/o*100}')
    echo "| $f | $orig | $sz | $ratio |" >> REPORT.md
  done
done

cat >> REPORT.md <<'EOF'

## split（1 MB 分卷）/ 大小

| 卷组 | 总大小 | 卷数 |
|------|--------|------|
EOF

for pair in "${KINDS[@]}"; do
  set -- $pair
  kind=$1
  for base in $(find "split/$kind" -type f | sort | sed -E 's/\.(part[0-9]+\.rar|[0-9]{3})$//' | sort -u); do
    total=$(find "split/$kind" -type f -name "$(basename "$base")*" -exec stat -f%z {} + | awk '{s+=$1} END{print s}')
    count=$(find "split/$kind" -type f -name "$(basename "$base")*" | wc -l | tr -d ' ')
    echo "| $base.* | $total | $count |" >> REPORT.md
  done
done

echo "REPORT.md 已生成"
