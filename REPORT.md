# 压缩对比报告

## 原始文件

| 文件 | 大小 (字节) | SHA-256 |
|------|------------|---------|
| rawfile1 | 1113 | da819b59140f5ee6a20e41029bd74cb8c428fb9871c2eb7d7e17e74a26d12f8a |
| rawfile2 | 9383744 | 8c34362cad802bf8253433f755e8806b24f500fd63d38cc4ec6fe0bb948a4fd2 |
| rawfile3 | 32333779 | 4afbb5cf52ecb94c99fd38241345f37eb2896382a1c977c72b2d194ed218642f |
| rawfile4 | 31360054 | 0577d33281a7c31aa92a4dd5836adc73455bc13d313c23309daaf7f06dc1474f |
| rawfile5 | 1572864 | 3072bf8024882ec3ccf419594cc3ec27247dffe7814194185aff086df0945682 |
| rawfile6 | 1950287 | 6f18f709786bb2e6f0d1305c58bbdd5ffd921be700348aa95dac6df170dd6a65 |
| rawfile7 | 1424458 | 06a9b4ba381f94965782e302ceddfe7294fde3c3619bc1b938d0143662e0cbc4 |
| rawfile8 | 1467889 | 5b98246f3147edf5bfb0e109b5f8d1bb109d4d264c0efe693feeb909c15e58f0 |
| combination | 79494188 | e1352260c8dd832f7cd812def585faa9539a2fffc76986fa2919d548c58e9df8 |

## 说明
- `rawfile1.txt`（1.1 KB）：文本，高度可压缩（莎士比亚《罗密欧与朱丽叶》节选）
- `rawfile2.jpg`（9.4 MB）：已压缩图片，近乎不可压
- `rawfile3.txt`（30.8 MB）：Gutenberg 公版英文书拼接，高度可压缩
- `rawfile4.bmp`（29.9 MB）：NASA 公版月球照片转 32 位 RGBA 位图，半可压
- `rawfile5.bin`（1.5 MB）：真随机数据，完全不可压
- `rawfile6.json`（1.9 MB）：结构化 JSON 记录，中等可压
- `rawfile7.c`（1.4 MB）：合成 C 源码，中等可压
- `rawfile8.fa`（1.4 MB）：DNA 序列（FASTA 格式），高可压
- `combination.bin`（全部文件拼接）：作为组合测试输入

档位策略：
- `rawfile1` / `rawfile2` / `rawfile5` ~ `rawfile8`：全档位（多等级）
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
| normal/rawfile5/rawfile5.b1.bz2 | 1572864 | 1585619 | 100.81% |
| normal/rawfile5/rawfile5.b9.bz2 | 1572864 | 1580605 | 100.49% |
| normal/rawfile5/rawfile5.br1.br | 1572864 | 1572875 | 100.00% |
| normal/rawfile5/rawfile5.br6.br | 1572864 | 1572872 | 100.00% |
| normal/rawfile5/rawfile5.br9.br | 1572864 | 1572872 | 100.00% |
| normal/rawfile5/rawfile5.g1.gz | 1572864 | 1573375 | 100.03% |
| normal/rawfile5/rawfile5.g6.gz | 1572864 | 1573375 | 100.03% |
| normal/rawfile5/rawfile5.g9.gz | 1572864 | 1573375 | 100.03% |
| normal/rawfile5/rawfile5.l1.lzma | 1572864 | 1595662 | 101.45% |
| normal/rawfile5/rawfile5.l9.lzma | 1572864 | 1594318 | 101.36% |
| normal/rawfile5/rawfile5.lz4-1.lz4 | 1572864 | 1572883 | 100.00% |
| normal/rawfile5/rawfile5.lz4-12.lz4 | 1572864 | 1572883 | 100.00% |
| normal/rawfile5/rawfile5.lz4-9.lz4 | 1572864 | 1572883 | 100.00% |
| normal/rawfile5/rawfile5.m1.rar | 1572864 | 1573032 | 100.01% |
| normal/rawfile5/rawfile5.m3.rar | 1572864 | 1573032 | 100.01% |
| normal/rawfile5/rawfile5.m5.rar | 1572864 | 1573032 | 100.01% |
| normal/rawfile5/rawfile5.mx1.7z | 1572864 | 1573082 | 100.01% |
| normal/rawfile5/rawfile5.mx5.7z | 1572864 | 1573079 | 100.01% |
| normal/rawfile5/rawfile5.mx9.7z | 1572864 | 1573079 | 100.01% |
| normal/rawfile5/rawfile5.x1.xz | 1572864 | 1573008 | 100.01% |
| normal/rawfile5/rawfile5.x6.xz | 1572864 | 1573008 | 100.01% |
| normal/rawfile5/rawfile5.x9.xz | 1572864 | 1573008 | 100.01% |
| normal/rawfile5/rawfile5.z1.zip | 1572864 | 1573278 | 100.03% |
| normal/rawfile5/rawfile5.z6.zip | 1572864 | 1573278 | 100.03% |
| normal/rawfile5/rawfile5.z9.zip | 1572864 | 1573278 | 100.03% |
| normal/rawfile5/rawfile5.zst-1.zst | 1572864 | 1572914 | 100.00% |
| normal/rawfile5/rawfile5.zst-19.zst | 1572864 | 1572913 | 100.00% |
| normal/rawfile5/rawfile5.zst-22.zst | 1572864 | 1572913 | 100.00% |
| normal/rawfile6/rawfile6.b1.bz2 | 1950287 | 316470 | 16.23% |
| normal/rawfile6/rawfile6.b9.bz2 | 1950287 | 302736 | 15.52% |
| normal/rawfile6/rawfile6.br1.br | 1950287 | 490100 | 25.13% |
| normal/rawfile6/rawfile6.br6.br | 1950287 | 390848 | 20.04% |
| normal/rawfile6/rawfile6.br9.br | 1950287 | 384246 | 19.70% |
| normal/rawfile6/rawfile6.g1.gz | 1950287 | 497761 | 25.52% |
| normal/rawfile6/rawfile6.g6.gz | 1950287 | 406721 | 20.85% |
| normal/rawfile6/rawfile6.g9.gz | 1950287 | 399840 | 20.50% |
| normal/rawfile6/rawfile6.l1.lzma | 1950287 | 419808 | 21.53% |
| normal/rawfile6/rawfile6.l9.lzma | 1950287 | 345783 | 17.73% |
| normal/rawfile6/rawfile6.lz4-1.lz4 | 1950287 | 695596 | 35.67% |
| normal/rawfile6/rawfile6.lz4-12.lz4 | 1950287 | 525554 | 26.95% |
| normal/rawfile6/rawfile6.lz4-9.lz4 | 1950287 | 528938 | 27.12% |
| normal/rawfile6/rawfile6.m1.rar | 1950287 | 481105 | 24.67% |
| normal/rawfile6/rawfile6.m3.rar | 1950287 | 410327 | 21.04% |
| normal/rawfile6/rawfile6.m5.rar | 1950287 | 403239 | 20.68% |
| normal/rawfile6/rawfile6.mx1.7z | 1950287 | 411165 | 21.08% |
| normal/rawfile6/rawfile6.mx5.7z | 1950287 | 361357 | 18.53% |
| normal/rawfile6/rawfile6.mx9.7z | 1950287 | 347056 | 17.80% |
| normal/rawfile6/rawfile6.x1.xz | 1950287 | 419916 | 21.53% |
| normal/rawfile6/rawfile6.x6.xz | 1950287 | 345884 | 17.74% |
| normal/rawfile6/rawfile6.x9.xz | 1950287 | 345884 | 17.74% |
| normal/rawfile6/rawfile6.z1.zip | 1950287 | 497670 | 25.52% |
| normal/rawfile6/rawfile6.z6.zip | 1950287 | 408626 | 20.95% |
| normal/rawfile6/rawfile6.z9.zip | 1950287 | 401802 | 20.60% |
| normal/rawfile6/rawfile6.zst-1.zst | 1950287 | 453341 | 23.24% |
| normal/rawfile6/rawfile6.zst-19.zst | 1950287 | 364533 | 18.69% |
| normal/rawfile6/rawfile6.zst-22.zst | 1950287 | 364478 | 18.69% |
| normal/rawfile7/rawfile7.b1.bz2 | 1424458 | 139873 | 9.82% |
| normal/rawfile7/rawfile7.b9.bz2 | 1424458 | 116446 | 8.17% |
| normal/rawfile7/rawfile7.br1.br | 1424458 | 324799 | 22.80% |
| normal/rawfile7/rawfile7.br6.br | 1424458 | 241369 | 16.94% |
| normal/rawfile7/rawfile7.br9.br | 1424458 | 211135 | 14.82% |
| normal/rawfile7/rawfile7.g1.gz | 1424458 | 353497 | 24.82% |
| normal/rawfile7/rawfile7.g6.gz | 1424458 | 243780 | 17.11% |
| normal/rawfile7/rawfile7.g9.gz | 1424458 | 237753 | 16.69% |
| normal/rawfile7/rawfile7.l1.lzma | 1424458 | 289978 | 20.36% |
| normal/rawfile7/rawfile7.l9.lzma | 1424458 | 180357 | 12.66% |
| normal/rawfile7/rawfile7.lz4-1.lz4 | 1424458 | 494133 | 34.69% |
| normal/rawfile7/rawfile7.lz4-12.lz4 | 1424458 | 271733 | 19.08% |
| normal/rawfile7/rawfile7.lz4-9.lz4 | 1424458 | 283080 | 19.87% |
| normal/rawfile7/rawfile7.m1.rar | 1424458 | 299346 | 21.01% |
| normal/rawfile7/rawfile7.m3.rar | 1424458 | 219622 | 15.42% |
| normal/rawfile7/rawfile7.m5.rar | 1424458 | 200737 | 14.09% |
| normal/rawfile7/rawfile7.mx1.7z | 1424458 | 274656 | 19.28% |
| normal/rawfile7/rawfile7.mx5.7z | 1424458 | 198046 | 13.90% |
| normal/rawfile7/rawfile7.mx9.7z | 1424458 | 180313 | 12.66% |
| normal/rawfile7/rawfile7.x1.xz | 1424458 | 290072 | 20.36% |
| normal/rawfile7/rawfile7.x6.xz | 1424458 | 180428 | 12.67% |
| normal/rawfile7/rawfile7.x9.xz | 1424458 | 180428 | 12.67% |
| normal/rawfile7/rawfile7.z1.zip | 1424458 | 353422 | 24.81% |
| normal/rawfile7/rawfile7.z6.zip | 1424458 | 243828 | 17.12% |
| normal/rawfile7/rawfile7.z9.zip | 1424458 | 237791 | 16.69% |
| normal/rawfile7/rawfile7.zst-1.zst | 1424458 | 295409 | 20.74% |
| normal/rawfile7/rawfile7.zst-19.zst | 1424458 | 180745 | 12.69% |
| normal/rawfile7/rawfile7.zst-22.zst | 1424458 | 180745 | 12.69% |
| normal/rawfile8/rawfile8.b1.bz2 | 1467889 | 425411 | 28.98% |
| normal/rawfile8/rawfile8.b9.bz2 | 1467889 | 423280 | 28.84% |
| normal/rawfile8/rawfile8.br1.br | 1467889 | 484679 | 33.02% |
| normal/rawfile8/rawfile8.br6.br | 1467889 | 454340 | 30.95% |
| normal/rawfile8/rawfile8.br9.br | 1467889 | 444525 | 30.28% |
| normal/rawfile8/rawfile8.g1.gz | 1467889 | 516513 | 35.19% |
| normal/rawfile8/rawfile8.g6.gz | 1467889 | 455792 | 31.05% |
| normal/rawfile8/rawfile8.g9.gz | 1467889 | 445175 | 30.33% |
| normal/rawfile8/rawfile8.l1.lzma | 1467889 | 468353 | 31.91% |
| normal/rawfile8/rawfile8.l9.lzma | 1467889 | 416706 | 28.39% |
| normal/rawfile8/rawfile8.lz4-1.lz4 | 1467889 | 841823 | 57.35% |
| normal/rawfile8/rawfile8.lz4-12.lz4 | 1467889 | 568741 | 38.75% |
| normal/rawfile8/rawfile8.lz4-9.lz4 | 1467889 | 601017 | 40.94% |
| normal/rawfile8/rawfile8.m1.rar | 1467889 | 470781 | 32.07% |
| normal/rawfile8/rawfile8.m3.rar | 1467889 | 452113 | 30.80% |
| normal/rawfile8/rawfile8.m5.rar | 1467889 | 445115 | 30.32% |
| normal/rawfile8/rawfile8.mx1.7z | 1467889 | 463270 | 31.56% |
| normal/rawfile8/rawfile8.mx5.7z | 1467889 | 416464 | 28.37% |
| normal/rawfile8/rawfile8.mx9.7z | 1467889 | 416696 | 28.39% |
| normal/rawfile8/rawfile8.x1.xz | 1467889 | 468472 | 31.91% |
| normal/rawfile8/rawfile8.x6.xz | 1467889 | 416816 | 28.40% |
| normal/rawfile8/rawfile8.x9.xz | 1467889 | 416816 | 28.40% |
| normal/rawfile8/rawfile8.z1.zip | 1467889 | 516312 | 35.17% |
| normal/rawfile8/rawfile8.z6.zip | 1467889 | 455615 | 31.04% |
| normal/rawfile8/rawfile8.z9.zip | 1467889 | 445118 | 30.32% |
| normal/rawfile8/rawfile8.zst-1.zst | 1467889 | 475698 | 32.41% |
| normal/rawfile8/rawfile8.zst-19.zst | 1467889 | 419743 | 28.60% |
| normal/rawfile8/rawfile8.zst-22.zst | 1467889 | 419743 | 28.60% |
| normal/combination/combination.b9.bz2 | 79494188 | 29337138 | 36.90% |
| normal/combination/combination.br9.br | 79494188 | 32375563 | 40.73% |
| normal/combination/combination.g9.gz | 79494188 | 37091341 | 46.66% |
| normal/combination/combination.l9.lzma | 79494188 | 28301137 | 35.60% |
| normal/combination/combination.lz4-9.lz4 | 79494188 | 41529875 | 52.24% |
| normal/combination/combination.m5.rar | 79494188 | 28440592 | 35.78% |
| normal/combination/combination.mx9.7z | 79494188 | 28248684 | 35.54% |
| normal/combination/combination.x9.xz | 79494188 | 28251116 | 35.54% |
| normal/combination/combination.z9.zip | 79494188 | 37091331 | 46.66% |
| normal/combination/combination.zst-19.zst | 79494188 | 30858397 | 38.82% |

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
| password/rawfile5/rawfile5.m1.rar | 1572864 | 1574862 | 100.13% |
| password/rawfile5/rawfile5.m3.rar | 1572864 | 1576286 | 100.22% |
| password/rawfile5/rawfile5.m5.rar | 1572864 | 1576286 | 100.22% |
| password/rawfile5/rawfile5.mx1.7z | 1572864 | 1573186 | 100.02% |
| password/rawfile5/rawfile5.mx5.7z | 1572864 | 1573186 | 100.02% |
| password/rawfile5/rawfile5.mx9.7z | 1572864 | 1573186 | 100.02% |
| password/rawfile5/rawfile5.z1.zip | 1572864 | 1573306 | 100.03% |
| password/rawfile5/rawfile5.z6.zip | 1572864 | 1573306 | 100.03% |
| password/rawfile5/rawfile5.z9.zip | 1572864 | 1573306 | 100.03% |
| password/rawfile6/rawfile6.m1.rar | 1950287 | 481438 | 24.69% |
| password/rawfile6/rawfile6.m3.rar | 1950287 | 410654 | 21.06% |
| password/rawfile6/rawfile6.m5.rar | 1950287 | 403566 | 20.69% |
| password/rawfile6/rawfile6.mx1.7z | 1950287 | 411266 | 21.09% |
| password/rawfile6/rawfile6.mx5.7z | 1950287 | 361458 | 18.53% |
| password/rawfile6/rawfile6.mx9.7z | 1950287 | 347154 | 17.80% |
| password/rawfile6/rawfile6.z1.zip | 1950287 | 497698 | 25.52% |
| password/rawfile6/rawfile6.z6.zip | 1950287 | 408654 | 20.95% |
| password/rawfile6/rawfile6.z9.zip | 1950287 | 401830 | 20.60% |
| password/rawfile7/rawfile7.m1.rar | 1424458 | 299678 | 21.04% |
| password/rawfile7/rawfile7.m3.rar | 1424458 | 219966 | 15.44% |
| password/rawfile7/rawfile7.m5.rar | 1424458 | 201070 | 14.12% |
| password/rawfile7/rawfile7.mx1.7z | 1424458 | 274754 | 19.29% |
| password/rawfile7/rawfile7.mx5.7z | 1424458 | 198146 | 13.91% |
| password/rawfile7/rawfile7.mx9.7z | 1424458 | 180418 | 12.67% |
| password/rawfile7/rawfile7.z1.zip | 1424458 | 353450 | 24.81% |
| password/rawfile7/rawfile7.z6.zip | 1424458 | 243856 | 17.12% |
| password/rawfile7/rawfile7.z9.zip | 1424458 | 237819 | 16.70% |
| password/rawfile8/rawfile8.m1.rar | 1467889 | 471118 | 32.09% |
| password/rawfile8/rawfile8.m3.rar | 1467889 | 452446 | 30.82% |
| password/rawfile8/rawfile8.m5.rar | 1467889 | 445454 | 30.35% |
| password/rawfile8/rawfile8.mx1.7z | 1467889 | 463378 | 31.57% |
| password/rawfile8/rawfile8.mx5.7z | 1467889 | 416562 | 28.38% |
| password/rawfile8/rawfile8.mx9.7z | 1467889 | 416802 | 28.39% |
| password/rawfile8/rawfile8.z1.zip | 1467889 | 516340 | 35.18% |
| password/rawfile8/rawfile8.z6.zip | 1467889 | 455643 | 31.04% |
| password/rawfile8/rawfile8.z9.zip | 1467889 | 445146 | 30.33% |
| password/combination/combination.m5.rar | 79494188 | 28440910 | 35.78% |
| password/combination/combination.mx9.7z | 79494188 | 28248787 | 35.54% |
| password/combination/combination.z9.zip | 79494188 | 37091359 | 46.66% |

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
| split/rawfile5/rawfile5.m1.* | 1574699 | 2 |
| split/rawfile5/rawfile5.m3.* | 1576123 | 2 |
| split/rawfile5/rawfile5.m5.* | 1576123 | 2 |
| split/rawfile5/rawfile5.mx1.7z.* | 1573082 | 2 |
| split/rawfile5/rawfile5.mx5.7z.* | 1573079 | 2 |
| split/rawfile5/rawfile5.mx9.7z.* | 1573079 | 2 |
| split/rawfile6/rawfile6.m1.rar.* | 481105 | 1 |
| split/rawfile6/rawfile6.m3.rar.* | 410327 | 1 |
| split/rawfile6/rawfile6.m5.rar.* | 403239 | 1 |
| split/rawfile6/rawfile6.mx1.7z.* | 411165 | 1 |
| split/rawfile6/rawfile6.mx5.7z.* | 361357 | 1 |
| split/rawfile6/rawfile6.mx9.7z.* | 347056 | 1 |
| split/rawfile7/rawfile7.m1.rar.* | 299346 | 1 |
| split/rawfile7/rawfile7.m3.rar.* | 219622 | 1 |
| split/rawfile7/rawfile7.m5.rar.* | 200737 | 1 |
| split/rawfile7/rawfile7.mx1.7z.* | 274656 | 1 |
| split/rawfile7/rawfile7.mx5.7z.* | 198046 | 1 |
| split/rawfile7/rawfile7.mx9.7z.* | 180313 | 1 |
| split/rawfile8/rawfile8.m1.rar.* | 470781 | 1 |
| split/rawfile8/rawfile8.m3.rar.* | 452113 | 1 |
| split/rawfile8/rawfile8.m5.rar.* | 445115 | 1 |
| split/rawfile8/rawfile8.mx1.7z.* | 463270 | 1 |
| split/rawfile8/rawfile8.mx5.7z.* | 416464 | 1 |
| split/rawfile8/rawfile8.mx9.7z.* | 416696 | 1 |
| split/combination/combination.m5.* | 28445855 | 29 |
| split/combination/combination.mx9.7z.* | 28248684 | 27 |
