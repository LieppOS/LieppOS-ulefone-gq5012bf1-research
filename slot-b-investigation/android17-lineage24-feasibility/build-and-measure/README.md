# Build and measure: LineageOS 24.0 Android 17 ARM64 GSI

Host-only continuation of research commit
`f732ff40287aa0d351dde0abe0b883a65f78a534`.

## Result

```text
BUILD_SUCCEEDED=1
TARGET=lineage_gsi_arm64 cp2a userdebug
FOLDED_LAYOUT=1
FILESYSTEM=EROFS (lz4hc level 9)
```

The official vanilla target produced one raw, AVB-footed `system.img`:

```text
path=/mnt/SamsungSSD/TIER3/phase5/android17/out-lineage_gsi_arm64-erofs/target/product/generic_arm64/system.img
size=1745326080
sha256=bae4ace2108d50bf431b9b49ccc3767e2867cb90e8290921c142d3df0c396eda
```

No physical `system_ext.img` or `product.img` exists: both trees are folded into
`/system/system_ext` and `/system/product`. No boot, vendor_boot, init_boot,
super, target-files or OTA tools artifact was requested by the smallest useful
`systemimage` build.

## Real footprint result

The built filesystem was extracted read-only and its three logical trees were
repacked separately with the same EROFS compressor. Minimal flags-0 AVB
hashtree/FEC partition sizes were then measured:

| Partition | Logical payload bytes | Measured EROFS | Required with AVB | Current B extent | Headroom | Fits |
|---|---:|---:|---:|---:|---:|---:|
| system | 1152368951 | 789716992 | 802463744 | 665391104 | -137072640 | 0 |
| system_ext | 627951987 | 360488960 | 366354432 | 366891008 | 536576 | 1* |
| product | 500596070 | 350040064 | 355741696 | 337686528 | -18055168 | 0 |

`*` system_ext fits the measurement by only 536,576 bytes. Exact Android
ownership/xattr metadata in a true split build could consume that margin, so it
is not production-proven.

```text
TOTAL_CURRENT_B_EXTENTS=1369968640
TOTAL_ANDROID17_REQUIRED=1524559872
EXTRA_BYTES_REQUIRED=154591232
```

The generic folded image itself is 1,745,326,080 bytes and cannot be placed in
`system_b`. Its large final size includes 221,006,144 bytes of AVB partition
padding outside the 1,500,532,736-byte EROFS area; sparse file size was not used
for fit calculations.

## Decision

Proceed to a proper split `lineage_gq5012bf1` product now. Keep this generic
image only as a future DSU framework/vendor proof with isolated guest userdata.
The split product should keep only VNDK 34, omit universal-GSI/debug payload,
remove measured optional apps/media, and remeasure all three independently.

## Files

- [`BUILD-ENVIRONMENT.md`](BUILD-ENVIRONMENT.md)
- [`BUILD-LOG-SUMMARY.md`](BUILD-LOG-SUMMARY.md)
- [`OUTPUT-ARTIFACTS.tsv`](OUTPUT-ARTIFACTS.tsv)
- [`IMAGE-SIZE-BREAKDOWN.tsv`](IMAGE-SIZE-BREAKDOWN.tsv)
- [`ANDROID17-PARTITION-FIT.tsv`](ANDROID17-PARTITION-FIT.tsv)
- [`FOLDED-LAYOUT.md`](FOLDED-LAYOUT.md)
- [`SIZE-OPTIMIZATION.md`](SIZE-OPTIMIZATION.md)
- [`DATABASE-GENERATIONS.md`](DATABASE-GENERATIONS.md)
- [`NEXT-BUILD-PLAN.md`](NEXT-BUILD-PLAN.md)

No phone command was issued. Nothing was flashed or activated, and all phone
partitions and data remain untouched.
