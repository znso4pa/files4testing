# 压缩对比报告

## 原始文件

| 文件 | 大小 (字节) | SHA-256 |
|------|------------|---------|
| rawfile1 | 1113 | da819b59140f5ee6a20e41029bd74cb8c428fb9871c2eb7d7e17e74a26d12f8a |
| rawfile2 | 9383744 | 8c34362cad802bf8253433f755e8806b24f500fd63d38cc4ec6fe0bb948a4fd2 |
| rawfile3 | 32333779 | 4afbb5cf52ecb94c99fd38241345f37eb2896382a1c977c72b2d194ed218642f |
| rawfile4 | 31360054 | 0577d33281a7c31aa92a4dd5836adc73455bc13d313c23309daaf7f06dc1474f |
| combination | 73078690 | f9b82162bd2e292b2caa5b9bfaf45947ac63daf5f6ad4ea2b75273613e154694 |

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
| normal/rawfile1/rawfile1.b1.bz2 | 1113 | 633 | 56.87% |
| normal/rawfile1/rawfile1.b9.bz2 | 1113 | 633 | 56.87% |
| normal/rawfile1/rawfile1.br1.br | 1113 | 665 | 59.75% |
| normal/rawfile1/rawfile1.br6.br | 1113 | 595 | 53.46% |
| normal/rawfile1/rawfile1.br9.br | 1113 | 596 | 53.55% |
| normal/rawfile1/rawfile1.g1.gz | 1113 | 651 | 58.49% |
| normal/rawfile1/rawfile1.g6.gz | 1113 | 639 | 57.41% |
| normal/rawfile1/rawfile1.g9.gz | 1113 | 639 | 57.41% |
| normal/rawfile1/rawfile1.l1.lzma | 1113 | 693 | 62.26% |
| normal/rawfile1/rawfile1.l9.lzma | 1113 | 687 | 61.73% |
| normal/rawfile1/rawfile1.lz4-1.lz4 | 1113 | 927 | 83.29% |
| normal/rawfile1/rawfile1.lz4-12.lz4 | 1113 | 909 | 81.67% |
| normal/rawfile1/rawfile1.lz4-9.lz4 | 1113 | 909 | 81.67% |
| normal/rawfile1/rawfile1.m1.rar | 1113 | 716 | 64.33% |
| normal/rawfile1/rawfile1.m3.rar | 1113 | 721 | 64.78% |
| normal/rawfile1/rawfile1.m5.rar | 1113 | 721 | 64.78% |
| normal/rawfile1/rawfile1.mx1.7z | 1113 | 812 | 72.96% |
| normal/rawfile1/rawfile1.mx5.7z | 1113 | 805 | 72.33% |
| normal/rawfile1/rawfile1.mx9.7z | 1113 | 806 | 72.42% |
| normal/rawfile1/rawfile1.x1.xz | 1113 | 748 | 67.21% |
| normal/rawfile1/rawfile1.x6.xz | 1113 | 740 | 66.49% |
| normal/rawfile1/rawfile1.x9.xz | 1113 | 740 | 66.49% |
| normal/rawfile1/rawfile1.z1.zip | 1113 | 794 | 71.34% |
| normal/rawfile1/rawfile1.z6.zip | 1113 | 782 | 70.26% |
| normal/rawfile1/rawfile1.z9.zip | 1113 | 782 | 70.26% |
| normal/rawfile1/rawfile1.zst-1.zst | 1113 | 656 | 58.94% |
| normal/rawfile1/rawfile1.zst-19.zst | 1113 | 631 | 56.69% |
| normal/rawfile1/rawfile1.zst-22.zst | 1113 | 631 | 56.69% |
| normal/rawfile2/rawfile2.b1.bz2 | 9383744 | 9346677 | 99.60% |
| normal/rawfile2/rawfile2.b9.bz2 | 9383744 | 9341365 | 99.55% |
| normal/rawfile2/rawfile2.br1.br | 9383744 | 9361808 | 99.77% |
| normal/rawfile2/rawfile2.br6.br | 9383744 | 9383761 | 100.00% |
| normal/rawfile2/rawfile2.br9.br | 9383744 | 9383761 | 100.00% |
| normal/rawfile2/rawfile2.g1.gz | 9383744 | 9339856 | 99.53% |
| normal/rawfile2/rawfile2.g6.gz | 9383744 | 9344539 | 99.58% |
| normal/rawfile2/rawfile2.g9.gz | 9383744 | 9344539 | 99.58% |
| normal/rawfile2/rawfile2.l1.lzma | 9383744 | 9399998 | 100.17% |
| normal/rawfile2/rawfile2.l9.lzma | 9383744 | 9380768 | 99.97% |
| normal/rawfile2/rawfile2.lz4-1.lz4 | 9383744 | 9383771 | 100.00% |
| normal/rawfile2/rawfile2.lz4-12.lz4 | 9383744 | 9383771 | 100.00% |
| normal/rawfile2/rawfile2.lz4-9.lz4 | 9383744 | 9383771 | 100.00% |
| normal/rawfile2/rawfile2.m1.rar | 9383744 | 9346533 | 99.60% |
| normal/rawfile2/rawfile2.m3.rar | 9383744 | 9357289 | 99.72% |
| normal/rawfile2/rawfile2.m5.rar | 9383744 | 9357288 | 99.72% |
| normal/rawfile2/rawfile2.mx1.7z | 9383744 | 9351146 | 99.65% |
| normal/rawfile2/rawfile2.mx5.7z | 9383744 | 9346466 | 99.60% |
| normal/rawfile2/rawfile2.mx9.7z | 9383744 | 9346432 | 99.60% |
| normal/rawfile2/rawfile2.x1.xz | 9383744 | 9353760 | 99.68% |
| normal/rawfile2/rawfile2.x6.xz | 9383744 | 9346816 | 99.61% |
| normal/rawfile2/rawfile2.x9.xz | 9383744 | 9346816 | 99.61% |
| normal/rawfile2/rawfile2.z1.zip | 9383744 | 9331070 | 99.44% |
| normal/rawfile2/rawfile2.z6.zip | 9383744 | 9336377 | 99.50% |
| normal/rawfile2/rawfile2.z9.zip | 9383744 | 9336382 | 99.50% |
| normal/rawfile2/rawfile2.zst-1.zst | 9383744 | 9366862 | 99.82% |
| normal/rawfile2/rawfile2.zst-19.zst | 9383744 | 9337998 | 99.51% |
| normal/rawfile2/rawfile2.zst-22.zst | 9383744 | 9337997 | 99.51% |
| normal/rawfile3/rawfile3.b9.bz2 | 32333779 | 8739528 | 27.03% |
| normal/rawfile3/rawfile3.br9.br | 32333779 | 9616028 | 29.74% |
| normal/rawfile3/rawfile3.g9.gz | 32333779 | 11899246 | 36.80% |
| normal/rawfile3/rawfile3.l9.lzma | 32333779 | 8240624 | 25.49% |
| normal/rawfile3/rawfile3.lz4-9.lz4 | 32333779 | 13705495 | 42.39% |
| normal/rawfile3/rawfile3.m5.rar | 32333779 | 8884979 | 27.48% |
| normal/rawfile3/rawfile3.mx9.7z | 32333779 | 8241570 | 25.49% |
| normal/rawfile3/rawfile3.x9.xz | 32333779 | 8241956 | 25.49% |
| normal/rawfile3/rawfile3.z9.zip | 32333779 | 11890184 | 36.77% |
| normal/rawfile3/rawfile3.zst-19.zst | 32333779 | 8768639 | 27.12% |
| normal/rawfile4/rawfile4.b9.bz2 | 31360054 | 8775865 | 27.98% |
| normal/rawfile4/rawfile4.br9.br | 31360054 | 10730602 | 34.22% |
| normal/rawfile4/rawfile4.g9.gz | 31360054 | 13186031 | 42.05% |
| normal/rawfile4/rawfile4.l9.lzma | 31360054 | 8156071 | 26.01% |
| normal/rawfile4/rawfile4.lz4-9.lz4 | 31360054 | 15440352 | 49.24% |
| normal/rawfile4/rawfile4.m5.rar | 31360054 | 7555389 | 24.09% |
| normal/rawfile4/rawfile4.mx9.7z | 31360054 | 8155763 | 26.01% |
| normal/rawfile4/rawfile4.x9.xz | 31360054 | 8157388 | 26.01% |
| normal/rawfile4/rawfile4.z9.zip | 31360054 | 13198370 | 42.09% |
| normal/rawfile4/rawfile4.zst-19.zst | 31360054 | 10185837 | 32.48% |
| normal/combination/combination.b9.bz2 | 73078690 | 26902440 | 36.81% |
| normal/combination/combination.br9.br | 73078690 | 29747991 | 40.71% |
| normal/combination/combination.g9.gz | 73078690 | 34432046 | 47.12% |
| normal/combination/combination.l9.lzma | 73078690 | 25763606 | 35.25% |
| normal/combination/combination.lz4-9.lz4 | 73078690 | 38536775 | 52.73% |
| normal/combination/combination.m5.rar | 73078690 | 25805371 | 35.31% |
| normal/combination/combination.mx9.7z | 73078690 | 25731702 | 35.21% |
| normal/combination/combination.x9.xz | 73078690 | 25733288 | 35.21% |
| normal/combination/combination.z9.zip | 73078690 | 34430399 | 47.11% |
| normal/combination/combination.zst-19.zst | 73078690 | 28311389 | 38.74% |

## password（密码：`123`）/ 压缩率

| 文件 | 原始大小 | 压缩后 | 压缩率 |
|------|---------|--------|--------|
| password/rawfile1/rawfile1.m1.rar | 1113 | 862 | 77.45% |
| password/rawfile1/rawfile1.m3.rar | 1113 | 878 | 78.89% |
| password/rawfile1/rawfile1.m5.rar | 1113 | 878 | 78.89% |
| password/rawfile1/rawfile1.mx1.7z | 1113 | 896 | 80.50% |
| password/rawfile1/rawfile1.mx5.7z | 1113 | 896 | 80.50% |
| password/rawfile1/rawfile1.mx9.7z | 1113 | 896 | 80.50% |
| password/rawfile1/rawfile1.z1.zip | 1113 | 822 | 73.85% |
| password/rawfile1/rawfile1.z6.zip | 1113 | 810 | 72.78% |
| password/rawfile1/rawfile1.z9.zip | 1113 | 810 | 72.78% |
| password/rawfile2/rawfile2.m1.rar | 9383744 | 9346862 | 99.61% |
| password/rawfile2/rawfile2.m3.rar | 9383744 | 9357614 | 99.72% |
| password/rawfile2/rawfile2.m5.rar | 9383744 | 9357614 | 99.72% |
| password/rawfile2/rawfile2.mx1.7z | 9383744 | 9351251 | 99.65% |
| password/rawfile2/rawfile2.mx5.7z | 9383744 | 9346563 | 99.60% |
| password/rawfile2/rawfile2.mx9.7z | 9383744 | 9346531 | 99.60% |
| password/rawfile2/rawfile2.z1.zip | 9383744 | 9331098 | 99.44% |
| password/rawfile2/rawfile2.z6.zip | 9383744 | 9336405 | 99.50% |
| password/rawfile2/rawfile2.z9.zip | 9383744 | 9336410 | 99.50% |
| password/rawfile3/rawfile3.m5.rar | 32333779 | 8885310 | 27.48% |
| password/rawfile3/rawfile3.mx9.7z | 32333779 | 8241667 | 25.49% |
| password/rawfile3/rawfile3.z9.zip | 32333779 | 11890212 | 36.77% |
| password/rawfile4/rawfile4.m5.rar | 31360054 | 7555710 | 24.09% |
| password/rawfile4/rawfile4.mx9.7z | 31360054 | 8155875 | 26.01% |
| password/rawfile4/rawfile4.z9.zip | 31360054 | 13198398 | 42.09% |
| password/combination/combination.m5.rar | 73078690 | 25805694 | 35.31% |
| password/combination/combination.mx9.7z | 73078690 | 25731795 | 35.21% |
| password/combination/combination.z9.zip | 73078690 | 34430427 | 47.11% |

## split（1 MB 分卷）/ 大小

| 卷组 | 总大小 | 卷数 |
|------|--------|------|
| split/rawfile1/rawfile1.m1.rar.* | 716 | 1 |
| split/rawfile1/rawfile1.m3.rar.* | 721 | 1 |
| split/rawfile1/rawfile1.m5.rar.* | 721 | 1 |
| split/rawfile1/rawfile1.mx1.7z.* | 812 | 1 |
| split/rawfile1/rawfile1.mx5.7z.* | 805 | 1 |
| split/rawfile1/rawfile1.mx9.7z.* | 806 | 1 |
| split/rawfile2/rawfile2.m1.* | 9348170 | 10 |
| split/rawfile2/rawfile2.m3.* | 9358926 | 10 |
| split/rawfile2/rawfile2.m5.* | 9358925 | 10 |
| split/rawfile2/rawfile2.mx1.7z.* | 9351146 | 9 |
| split/rawfile2/rawfile2.mx5.7z.* | 9346466 | 9 |
| split/rawfile2/rawfile2.mx9.7z.* | 9346432 | 9 |
| split/rawfile3/rawfile3.m5.* | 8886434 | 9 |
| split/rawfile3/rawfile3.mx9.7z.* | 8241570 | 8 |
| split/rawfile4/rawfile4.m5.* | 7556662 | 8 |
| split/rawfile4/rawfile4.mx9.7z.* | 8155763 | 8 |
| split/combination/combination.m5.* | 25810070 | 26 |
| split/combination/combination.mx9.7z.* | 25731702 | 25 |
