# Build environment

## Storage gate

Measured before starting:

| Item | Bytes |
|---|---:|
| free on `/mnt/SamsungSSD` | 235261165568 |
| required minimum (110 GiB) | 118111600640 |
| source tree | 200036133462 |
| phase5 artifact directory then | 17314459677 |
| artifact filesystem free | 235261165568 |

`STORAGE_GATE=PASS`. No file or source tree was deleted. After Git LFS
hydration, build and measurements, source usage was 200575493408 bytes and the
external phase5 directory was 146464678126 bytes.

## Source identity

```text
source=/mnt/SamsungSSD/android/lineage-24.0
manifest_branch=refs/heads/lineage-24.0
manifest_commit=f16772cb8c33a15e970abe42d7bb120e2dc84f33
repo_status_before=clean
repo_status_after=clean
Android=17
SDK=37
security_patch=2026-09-01
Lineage=24.0-20260928-UNOFFICIAL-gsi_arm64
build_id=CP2A.260605.016
```

No resync occurred. The only source-environment repair was hydrating the
manifest-selected ARM64 Chromium WebView Git LFS object; Git status remained
clean.

## Exact configuration

```sh
export OUT_DIR=out-android17-gsi-erofs
export GSI_FILE_SYSTEM_TYPE=erofs
export PATH=/mnt/SamsungSSD/TIER3/phase5/android17/tools/git-lfs-3.8.0:$HOME/bin:$PATH
cd /mnt/SamsungSSD/android/lineage-24.0
source build/envsetup.sh
lunch lineage_gsi_arm64 cp2a userdebug
m -j32 systemimage
```

The build shell was launched with:

```sh
numactl \
  --physcpubind=0-3,8-11,16-19,24-27,32-35,40-43,48-51,56-59 \
  --interleave=all \
  /mnt/SamsungSSD/TIER3/phase5/android17/build-gsi-erofs.sh
```

This selects 16 physical cores / 32 SMT threads across CPU NUMA nodes 0–3.
The host exposed memory-bearing nodes 0 and 2, so the inherited effective memory
policy was `interleave:0,2`.

## Configured build variables

| Variable | Value |
|---|---|
| `TARGET_PRODUCT` | `lineage_gsi_arm64` |
| release argument | `cp2a` |
| `TARGET_BUILD_VARIANT` | `userdebug` |
| `TARGET_ARCH` / second arch | `arm64` / `arm` |
| `PRODUCT_OUT` | `out-android17-gsi-erofs/target/product/generic_arm64` |
| `GSI_FILE_SYSTEM_TYPE` | `erofs` |
| `BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE` | `erofs` |
| EROFS default compressor | `lz4hc,9` |
| sparse EROFS output disabled | `true` |
| `TARGET_COPY_OUT_PRODUCT` | `system/product` |
| `TARGET_COPY_OUT_SYSTEM_EXT` | `system/system_ext` |
| dynamic partitions / dynamic size | `true` / `true` |
| dynamic partition list | `system` only |
| GSI dynamic group size | 3221225472 |
| super size | 3229614080 |
| `BOARD_AVB_ENABLE` | `true` |
| system AVB | SHA256_RSA2048, test key, SHA-256 hashtree |
| dexpreopt | enabled |
| kernel | `TARGET_NO_KERNEL=true` |

`BOARD_PRODUCTIMAGE_FILE_SYSTEM_TYPE` and
`BOARD_SYSTEM_EXTIMAGE_FILE_SYSTEM_TYPE` were empty because these images are
not built separately.
