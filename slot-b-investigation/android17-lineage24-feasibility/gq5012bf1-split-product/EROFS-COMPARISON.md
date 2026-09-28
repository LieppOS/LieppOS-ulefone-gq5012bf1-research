# EROFS comparison

## Identical frozen GSI payload

The extracted GSI was repacked into three trees with the build's
`mkfs.erofs 1.8.3`. This isolates pcluster effects from package changes.

| Logical image | `lz4hc,9`, default pcluster | `lz4hc,9`, 262144 pcluster | Saving | Saving % |
|---|---:|---:|---:|---:|
| system | 789716992 | 703225856 | 86491136 | 10.952% |
| system_ext | 360488960 | 299610112 | 60878848 | 16.888% |
| product | 350040064 | 296513536 | 53526528 | 15.291% |
| **Total** | **1500246016** | **1299349504** | **200896512** | **13.391%** |

With SHA-256 hashtree/FEC, the 256 KiB generic repack still needed 714584064
system bytes, 49,192,960 over `system_b`. Compression alone was not enough;
the real physical product also had to drop generic-only payload.

## Final device build

```text
BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE=erofs
BOARD_SYSTEM_EXTIMAGE_FILE_SYSTEM_TYPE=erofs
BOARD_PRODUCTIMAGE_FILE_SYSTEM_TYPE=erofs
BOARD_EROFS_COMPRESSOR=lz4hc,9
BOARD_EROFS_PCLUSTER_SIZE=262144
TARGET_USERIMAGES_SPARSE_EROFS_DISABLED=true
```

Final EROFS bytes are 625823744, 235327488, and 291459072. The first complete
split build took 01:23:27 on 16 physical cores / 32 SMT threads; the VINTF-only
rebuild took 07:42.

## Why not zstd

The built `fsck.erofs` reports decoding support for `lz4`, `lz4hc`, and
`deflate`, not zstd. The existing kernel/vendor evidence proves the current
EROFS/LZ4 path and does not prove an EROFS zstd decoder. Selecting zstd for size
alone would therefore be unsupported. Encoder level changes are unnecessary
because the measured configuration already fits all partitions.
