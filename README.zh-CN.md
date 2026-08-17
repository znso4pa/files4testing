# files4testing — 压缩测试向量

提供多个无版权原始文件，压缩为 **10 种格式 + 7 种 tar 变体 + ISO/CSO × 3 层**（normal / password / 分卷），供自己实现
解压器/压缩器（如 Rust）的人直接使用的、可机器校验的测试输入。v1.2 新增 ISO 9660 / CSO 向量、
多文件树归档、各格式特性变体，以及扫描器语料（`scan/`）。

> **注意：本 git 仓库很轻（仅脚本/文档/manifest），实际压缩文件托管在 GitHub Release
> （约 1.6 GB），见英文 README 的下载说明。**

## 原始文件

| 文件 | 大小 | 特性 |
|------|------|------|
| `rawfiles/rawfile1.txt` | 1.1 KB | 文本，高度可压缩（莎士比亚《罗密欧与朱丽叶》节选） |
| `rawfiles/rawfile2.jpg` | 9.4 MB | 已压缩图片，近乎不可压（测试算法对已压缩数据的处理） |
| `rawfiles/rawfile3.txt` | 30.8 MB | Gutenberg 公版英文书拼接，高度可压缩 |
| `rawfiles/rawfile4.bmp` | 29.9 MB | NASA 公版月球照片转 32 位 RGBA 位图，半可压 |
| `rawfiles/rawfile5.bin` | 1.5 MB | 真随机数据（urandom），完全不可压 |
| `rawfiles/rawfile6.json` | 1.9 MB | 结构化 JSON 记录，中等可压 |
| `rawfiles/rawfile7.c` | 1.4 MB | 合成 C 源码，中等可压 |
| `rawfiles/rawfile8.fa` | 1.4 MB | DNA 序列（FASTA），高可压 |
| `rawfiles/combination.bin` | ~76 MB | 以上全部文件拼接，作为组合测试输入 |

原始文件 SHA-256 见 `REPORT.md`，可用于校验解压结果是否正确。

## 目录结构

```
normal/    无加密无分卷（全部格式 × 多等级 + iso/cso + 树归档）
password/  加密，密码统一为 123（仅支持加密的格式：7z/zip/rar）
split/     1 MB 分卷（仅支持分卷的格式：7z/rar/zip）
  ├─ rawfile1/      rawfile1 单独压缩
  ├─ rawfile2/      rawfile2 单独压缩
  ├─ rawfile3/      rawfile3 单独压缩
  ├─ rawfile4/      rawfile4 单独压缩
  ├─ rawfile5/      rawfile5 单独压缩
  ├─ rawfile6/      rawfile6 单独压缩
  ├─ rawfile7/      rawfile7 单独压缩
  ├─ rawfile8/      rawfile8 单独压缩
  ├─ rawfile_tree/  多文件树归档（iso + tar + 压缩 tar）
  └─ combination/   combination.bin 压缩
faults/    负向用例（损坏 / 截断 / 错误密码 / 缺卷）
scan/      扫描器语料（非零偏移嵌入归档 + scan/manifest.json）
```

## 档位策略

| 文件 | 档位 |
|------|------|
| `rawfile1` / `rawfile2` / `rawfile5`–`rawfile8` | 全档位（每格式多个等级） |
| `rawfile3` / `rawfile4` / `combination` | 精简档位（每格式一个代表等级，控制体积） |

## 格式与等级

全档位文件（rawfile1 / rawfile2 / rawfile5–rawfile8）各格式等级：

| 格式 | 扩展名 | 等级 |
|------|--------|------|
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

v1.2 容器/方法变体（normal 层，默认 rawfile1）：

| 变体 | 向量 |
|------|------|
| iso | `rawfileN.iso`（单文件）、`rawfile_tree.iso`（多文件树） |
| cso | `rawfileN.iso.cso`（解压得到对应 `.iso` 字节流） |
| 7z 方法 | `mlzma`（LZMA）、`mppmd`（PPMd）、`mbz2`（BZip2）、`mcopy`（Copy）、`mbcj`（BCJ+LZMA2） |
| zip 方法 | `z0`（store）、`zbz2`（BZip2）、`zlzma`（LZMA）；AES-256 `zaes` 在 password/ |
| gzip | `g9.multi`（两个成员拼接） |
| zstd | `zst-nocheck`（无校验和）、`zst-nofcs`（无内容大小）、`zst-multi`（两帧） |
| xz | `xz-sha256`、`xz-block`（多块）、`xz-delta`（delta 滤镜）、`xz-x86`（BCJ 滤镜） |
| lz4 | `lz4-cs`（含内容大小）、`lz4-legacy`（legacy 帧） |
| lzma | `l9.size`（已知大小头部） |
| rar | `m0`（store）、`ms`（solid）；非固实为默认 |
| tar 树 | `rawfile_tree.tar[.g9.gz/.b9.bz2/.x9.xz/.zst-19.zst]` 多文件 + symlink |
| split zip | `rawfile2.zsplit.zip.001..`（1 MB 字节分卷） |

tar 系列（仅 normal 层，归档内只含该原始文件）：

| 格式 | 扩展名 | 等级 |
|------|--------|------|
| tar（纯归档） | `.tar.tar` | — |
| tar + gzip | `.tar.<lvl>.tar.gz` | g1 / g6 / g9 |
| tar + bzip2 | `.tar.<lvl>.tar.bz2` | b1 / b9 |
| tar + xz | `.tar.<lvl>.tar.xz` | x1 / x6 / x9 |
| tar + lzma | `.tar.<lvl>.tar.lzma` | l1 / l9 |
| tar + lz4 | `.tar.<lvl>.tar.lz4` | lz4-1 / lz4-9 / lz4-12 |
| tar + zstd | `.tar.<lvl>.tar.zst` | zst-1 / zst-19 / zst-22 |
| tar + brotli | `.tar.<lvl>.tar.br` | br1 / br6 / br9 |

精简档位文件（rawfile3 / rawfile4 / combination）每格式一个等级：
7z-mx9、zip-z9、rar-m5、gzip-g9、bzip2-b9、xz-x9、lzma-l9、lz4-lz4-9、zstd-zst-19、
以及 tar + 各压缩器最高档（tar.g9.tar.gz、tar.b9.tar.bz2、tar.x9.tar.xz、
tar.l9.tar.lzma、tar.lz4-9.tar.lz4、tar.zst-19.tar.zst、tar.br9.tar.br）。

## 命名规则

`<原始文件名>.<格式与等级>.<扩展名>`，例如 `rawfile1.mx9.7z`、`combination.zst-19.zst`。

## 密码

password 层所有文件密码为 `123`。7z 使用 `-mhe=on`（加密文件头），rar 使用 `-hp`。

## 分卷

split 层分卷大小为 1 MB：
- 7z：`.7z.001`、`.7z.002` ... 从 `.001` 开始解压
- rar：`.part01.rar`、`.part02.rar` ... 从 `part01` 开始解压
- zip：`.zip.001`、`.zip.002` ...（7-Zip 字节分卷，从 `.001` 开始）

## 负向用例（faults/）

正确的解压器必须**拒绝** `faults/` 中的每个文件（干净地失败，而不是崩溃或产出数据）：

| 类别 | 文件 |
|------|------|
| 截断 | `.gz` / `.xz` / `.7z` / `.rar` / `.zip` / `.zst` / `.lz4` / `.bz2` / `.br` / `.lzma` 各取一半 |
| 损坏 | 翻转中间字节（`.gz` / `.7z` / `.zip` / `.rar` / `.xz` / `.lzma`） |
| 错误密码 | 用错误密码打开 `password/` 归档 |
| 缺卷 | 只有 `.rar` 分卷的 `part01` / 只有 `.7z.001` |
| 空输入 | 零字节文件 |

`verify.sh` 会断言参考工具全部拒绝（`faults/manifest.json` 列出预期失败项）。

## 扫描器语料（scan/）

供 binwalk 式签名扫描器（如 [usefulunpack](https://github.com/znso4pa/usefulunpack) 的 `scan-core`）使用：

- 扫描器可识别的有效小文件：`rawfiles/rawfile_png.png`、`rawfile_gif.gif`、
  `rawfile_tiff.tiff`、`rawfile_pdf.pdf`、`rawfile_elf.elf`、`rawfile_wav.wav`、`rawfile_mpeg.mpeg`
- `scan/` 内**非零偏移嵌入归档**：有效 `gz`/`xz`/`lzma`/`zip` 前加 0x1000 字节垃圾，
  正确扫描器须在偏移 `0x1000` 报告
- `scan/manifest.json` 记录每项预期格式与偏移

注意：`verify.sh` 对 `cso` 条目标记 SKIP（macOS 无参考 CLI）；cso 正确性在生成期经回环校验，
并由消费方实现（如 `usefulunpack`）验证。

## 其他

- `normal/` 中的 `combination` 流式格式（gz/bz2/xz/lzma/lz4/zst）是对 `combination.bin` 直接压缩，与归档格式（7z/zip/rar）内容一致
- `compress.sh` 为生成脚本，`gen_v12.sh` 生成 v1.2 新增向量，`gen_scan.py` 生成扫描语料，`gen_report.sh` 重新生成 `REPORT.md`（含全部压缩率与 SHA-256）
- 参考 harness：`harness/`（Rust）、`harness_py/run.py`（Python）、`harness_go/`（Go）
- 压缩率对比见 `REPORT.md`

## 数据来源与许可

| 文件 | 来源 | 许可 |
|------|------|------|
| `rawfile1.txt` | 莎士比亚《罗密欧与朱丽叶》节选 | 公有领域 |
| `rawfile2.jpg` | 见 REPORT.md（无版权保护素材） | 公有领域 |
| `rawfile3.txt` | [Project Gutenberg](https://www.gutenberg.org/) 公版英文书拼接 | 公有领域（分发须遵守 Project Gutenberg 许可/商标条款） |
| `rawfile4.bmp` | [NASA PIA00405](https://images.nasa.gov/details/PIA00405)，Galileo 飞船 1992 年拍摄月球 | 公有领域 |
| `rawfile5.bin` | `/dev/urandom` 生成 | 生成数据（无版权） |
| `rawfile6.json` | 合成结构化记录 | 生成数据（无版权） |
| `rawfile7.c` | 合成 C 源码 | 生成数据（无版权） |
| `rawfile8.fa` | 合成 DNA（FASTA） | 生成数据（无版权） |

本仓库（脚本、文档、压缩产物）采用 **MIT License**，见 `LICENSE`。
压缩产物是对公有领域原始数据的无损变换，随原始数据一并归属公有领域。
