# Folded GSI layout

## Proof from configuration

```text
TARGET_COPY_OUT_PRODUCT=system/product
TARGET_COPY_OUT_SYSTEM_EXT=system/system_ext
BOARD_USES_PRODUCTIMAGE=<empty>
BOARD_USES_SYSTEM_EXTIMAGE=<empty>
BOARD_GSI_DYNAMIC_PARTITIONS_PARTITION_LIST=system
PRODUCT_USE_DYNAMIC_PARTITIONS=true
PRODUCT_USE_DYNAMIC_PARTITION_SIZE=true
```

Only `system.img` was emitted. `system_ext.img` and `product.img` are absent.

## Proof from the image

Read-only extraction with `fsck.erofs --extract` found:

```text
/product    -> /system/product
/system_ext -> /system/system_ext
```

The physical EROFS image therefore consists of:

| Logical owner | Physical path in folded image | Uncompressed pathname payload | Measured separate EROFS |
|---|---|---:|---:|
| system | root plus `/system`, excluding the two subtrees below | 1152368951 | 789716992 |
| system_ext | `/system/system_ext` | 627951987 | 360488960 |
| product | `/system/product` | 500596070 | 350040064 |

Payload includes regular-file bytes plus symlink text. Hardlinked paths are
counted by pathname; EROFS measurements—not payload sums—are used for fit.

## Measurement method

1. Validate and extract the built image read-only using the build's
   `fsck.erofs`; 7211 regular paths and 344 symlinks were recovered.
2. Repack the entire extraction with `mkfs.erofs -zlz4hc,level=9` as a control.
   Result: 1,500,160,000 bytes versus the production EROFS area
   1,500,532,736 bytes, a 372,736-byte (0.025%) difference.
3. Repack system with `system/product` and `system/system_ext` excluded, and
   repack those two subtrees independently.
4. Invert `avbtool add_hashtree_footer --calc_max_image_size` at 4096-byte
   alignment with SHA256_RSA2048, SHA-256 hashtree and two-root FEC.
5. Materialize flags-0 measurement images at the calculated minimum sizes and
   confirm each AVB footer parses.

The three separate EROFS images total 1,500,246,016 bytes—86,016 bytes larger
than the recompressed folded control due to separate filesystem metadata.

## Caveat

These are high-confidence footprint measurements, not final device artifacts.
The read-only extraction intentionally did not preserve privileged ownership or
SELinux xattrs. A true split product will regenerate exact fs_config/file
contexts. The full-control delta is small, but it matters for system_ext's
536,576-byte margin; system_ext must be given real headroom in the next build.
