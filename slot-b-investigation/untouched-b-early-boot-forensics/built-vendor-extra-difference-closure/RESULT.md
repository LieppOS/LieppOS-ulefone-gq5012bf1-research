# Built vendor incidental-difference closure

## Baselines

Current Slot-B vendor image:

`/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/slot-b-investigation/current-b-logical-dumps/vendor_b.img`

SHA256:

`9f3dfe3fe5ef025b667b8181bddfedaf6b08dace4b7cd6c4e05a4fde0d16aa98`

TIER3 staged vendor image:

`/mnt/SamsungSSD/TIER3/phase4/staging/complete-b-set/run-20260811T231651Z/vendor.img`

SHA256:

`9f3dfe3fe5ef025b667b8181bddfedaf6b08dace4b7cd6c4e05a4fde0d16aa98`

These are byte-identical.

Therefore the mounted/current-B vendor baseline and the TIER3 staged
`vendor.img` are the same image.

Built fixed vendor image:

`/mnt/SamsungSSD/android/lineage-22.2/out/target/product/armol/vendor.img`

SHA256:

`850a58b16357597e0fa93f7d5ab9443c85e1b49df33b0e86fa1d2d393044ca50`

## Required MT6878 configuration

The rebuilt image contains:

`/etc/init.insmod.mt6878.cfg`

with exact verified stock SHA256:

`683d5f45ddf50f6091ce5bbcf4b90d3e92b4bd5ebf05bebab0d59ccf8b112c98`

The current-B image does not contain the file.

## Complete logical filesystem delta

The previous comparison found three paths.

This audit independently re-extracted both actual EROFS images and reconfirmed:

`EXACT_EXPECTED_THREE_PATHS=1`

The paths are:

- `/etc/init.insmod.mt6878.cfg`
- `/etc/NOTICE.xml.gz`
- `/odm/etc/build.prop`

No fourth logical file difference exists.

## ODM build.prop

```text
OLD_PROPERTY_COUNT=19
NEW_PROPERTY_COUNT=19
CHANGED_PROPERTY_COUNT=3
NONPROPERTY_TEXT_SAME=1
BUILD_PROP_BUILD_METADATA_ONLY=1

CHANGED_PROPERTIES:
ro.odm.build.date
  CURRENT_B='Wed Aug 12 02:07:32 EEST 2026'
  BUILT='Fri Sep 18 14:42:57 EEST 2026'
ro.odm.build.date.utc
  CURRENT_B='1786489652'
  BUILT='1789731777'
ro.odm.build.version.incremental
  CURRENT_B='1786489652'
  BUILT='1789731777'
```

Classification:

`BUILD_PROP_BUILD_METADATA_ONLY=1`

The raw unified diff is stored in:

`odm-build-prop.diff`

## NOTICE.xml.gz

```json
{
  "built_compressed_sha256": "242b6b03af38eea06f4e1f5c12011d07056e2d697dc9743161f7004935269cfc",
  "built_compressed_size": 133136,
  "built_decompressed_sha256": "68eb8af243f8b01c660ed73aa20c05bac27c878ffcf50c244389efc64ba7629e",
  "built_decompressed_size": 1649797,
  "compressed_identical": false,
  "current_b_compressed_sha256": "b2c1db19543986e969e7fc4d85b1582457141d1391be15dfc2fb24e5751ece4b",
  "current_b_compressed_size": 133119,
  "current_b_decompressed_sha256": "7ff76725d5c79066befc85c75f55d549b498036653e35292b0681d467090d0ad",
  "current_b_decompressed_size": 1649680,
  "decompressed_identical": false,
  "unified_diff_line_count": 10
}
```

Boot/config reference count:

`0`

Runtime relevance classification:

`NOTICE_RUNTIME_RELEVANT=0`

The decompressed XML diff is stored in:

`notice-decompressed.diff`

## AVB image structure

```text
AVB_STATIC_STRUCTURE_MATCH=1
AVB_ROOT_DIGEST_CHANGED=1
IMAGE_SIZE_DELTA=4096
ORIGINAL_IMAGE_SIZE_DELTA=4096
```

The expected root digest difference is caused by changed filesystem content.

The unchanged AVB structural parameters include the hashtree algorithm,
partition name, salt, block sizes, FEC configuration, rollback settings and
other static descriptor parameters checked by this audit.

## Runtime-candidate classification

`NARROW_RUNTIME_CANDIDATE=1`

`RUNTIME_DIFFERENCE_CLASS=ONLY_REQUIRED_CFG_IS_FUNCTIONALLY_BOOT_RELEVANT`

If this classification is 1 / ONLY_REQUIRED_CFG_IS_FUNCTIONALLY_BOOT_RELEVANT,
the rebuilt vendor image has only one functionally boot-relevant difference
from current Slot B: restoration of the required MediaTek
`init.insmod.mt6878.cfg`.

The other rebuilt-image differences are generated build/legal metadata rather
than an independent boot-path change.

## Kernel warning

The prior successful vendor build's prebuilt-kernel warning remains classified
as expected bring-up technical debt.

It does not invalidate this vendor-image comparison.

## Safety

This entire closure audit was host-side.

No phone command was issued.

No partition was written.

No slot state was changed.

No runtime test was performed.

## Next phase

If the narrow runtime-candidate classification passes, source/content analysis
for this vendor fix is complete.

The next phase should inspect the exact Slot-B AVB descriptor chain and produce
the smallest AVB-consistent B-only replacement plan before any flash.
