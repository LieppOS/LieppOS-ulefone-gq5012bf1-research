# Build result

## Configuration

**PROVEN:** `lineage_gsi_arm64 cp2a userdebug` lunches with:

```text
Android=17
SDK=37
security_patch=2026-09-01
Lineage=24.0-20260927-UNOFFICIAL-gsi_arm64
BOARD_API_LEVEL=202604
PLATFORM_SEPOLICY_VERSION=202604
filesystem=ext4 (default)
BUILDING_GSI=true
BUILDING_LINEAGE_GSI=true
```

`m -j16 nothing` completed successfully in 08:07, including all 336 graph and
packaging-rule steps. This proves source parsing, product inheritance, Soong,
Make, license/SBOM graph and Ninja generation.

## Siso host issue and resolution

The first `m nothing` attempt used an absolute `OUT_DIR`. Siso 1.5.8 documents
`--config_repo_dir` as relative to the execution root; Soong passed the absolute
path and Siso looked for `main.star` incorrectly. No source was patched. A
source-root symlink to the external phase5 output and a relative
`OUT_DIR=out-android17-gsi` fixed it. The successful output still resides under
`/mnt/SamsungSSD/TIER3/phase5/android17/`.

## Full build gate

```text
BUILD_ATTEMPTED=0
BUILD_SUCCEEDED=0
```

**BLOCKER:** after graph generation, free space was only 57,484,259,328 bytes;
the conservative 150,000,000,000-byte build allowance was short by
92,515,740,672 bytes. Starting `m systemimage` would risk filling the shared
filesystem. The instruction not to delete existing trees takes precedence.

## Artifacts

No final `system.img`, `system_ext.img`, `product.img`, vbmeta, boot image,
target-files archive or otatools package was produced. Therefore filesystem,
logical size, SHA-256, footer and descriptor fields for Android 17 outputs are
**UNKNOWN / NOT BUILT**, not guessed.

Logs and build graph are outside Git:
`/mnt/SamsungSSD/TIER3/phase5/android17/`.
