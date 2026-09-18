# Built vendor image versus current Slot-B vendor

## Built image

Path:

`/mnt/SamsungSSD/android/lineage-22.2/out/target/product/armol/vendor.img`

Size:

`816353280`

SHA256:

`850a58b16357597e0fa93f7d5ab9443c85e1b49df33b0e86fa1d2d393044ca50`

Type:

`EROFS filesystem, compat: SB_CHKSUM MTIME, blocksize=12, exslots=0, uuid=c052e527-893b-5833-b105-149a2831daca, incompat: LZ4_0PADDING`

The image identity matches the successful BP1A vendorimage build.

## MT6878 insmod configuration in final EROFS image

The actual built `vendor.img` was extracted read-only.

The required file exists inside the final filesystem:

`/etc/init.insmod.mt6878.cfg`

SHA256:

`683d5f45ddf50f6091ce5bbcf4b90d3e92b4bd5ebf05bebab0d59ccf8b112c98`

Expected verified stock SHA256:

`683d5f45ddf50f6091ce5bbcf4b90d3e92b4bd5ebf05bebab0d59ccf8b112c98`

Result:

`VENDOR_IMAGE_CFG_EXACT=1`

This closes the source-versus-final-image distinction for the missing
MediaTek module-loader configuration.

## Current Slot-B vendor baseline

Mounted baseline:

`/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/slot-b-investigation/untouched-b-early-boot-forensics/b-mounts/vendor`

Mount source:

`/dev/loop3`

Resolved backing image:

`/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/slot-b-investigation/current-b-logical-dumps/vendor_b.img`

Backing image SHA256:

`9f3dfe3fe5ef025b667b8181bddfedaf6b08dace4b7cd6c4e05a4fde0d16aa98`

A temporary host-side snapshot was made with elevated read permission solely
to work around unreadable files such as `vendor/build.prop`.

The mounted source itself was not modified.

## Logical filesystem comparison

```json
{
  "added": 1,
  "built_entries": 2009,
  "changed": 2,
  "current_b_entries": 2008,
  "difference_count": 3,
  "only_expected_cfg_added": false,
  "removed": 0,
  "same": 2006,
  "type_changed": 0
}
```

Classification:

`BUILT_VENDOR_HAS_ADDITIONAL_LOGICAL_DIFFERENCES`

The complete difference list is stored in:

`built-vs-current-b-diff.tsv`

Boot-relevant differences are separately stored in:

`boot-relevant-differences.tsv`

## Built AVB metadata

```text
Footer version:           1.0
Image size:               816353280 bytes
Original image size:      800980992 bytes
VBMeta offset:            813682688
VBMeta size:              768 bytes
--
Minimum libavb version:   1.0
Header Block:             256 bytes
Authentication Block:     0 bytes
Auxiliary Block:          512 bytes
Algorithm:                NONE
Rollback Index:           0
Flags:                    0
Rollback Index Location:  0
Release String:           'avbtool 1.3.0'
Descriptors:
    Hashtree descriptor:
      Version of dm-verity:  1
      Image Size:            800980992 bytes
      Tree Offset:           800980992
      Tree Size:             6311936 bytes
      Data Block Size:       4096 bytes
      Hash Block Size:       4096 bytes
      FEC num roots:         2
      FEC offset:            807292928
      FEC size:              6389760 bytes
      Hash Algorithm:        sha1
      Partition Name:        vendor
      Salt:                  b6497d667c35b54999e4eee6d8c57a3e606fe5bf5d1c2e4919e201e5fb624aa6
      Root Digest:           4e290de2ea57b86baf081f1d248b8ad5ce568e9c
      Flags:                 0
    Prop: com.android.build.vendor.os_version -> '15'
    Prop: com.android.build.vendor.fingerprint -> 'Ulefone/lineage_armol/armol:15/BP1A.250505.005/eng.armol:userdebug/test-keys'
```

## Current-B backing-image AVB metadata

```text
Footer version:           1.0
Image size:               816349184 bytes
Original image size:      800976896 bytes
VBMeta offset:            813678592
VBMeta size:              768 bytes
--
Minimum libavb version:   1.0
Header Block:             256 bytes
Authentication Block:     0 bytes
Auxiliary Block:          512 bytes
Algorithm:                NONE
Rollback Index:           0
Flags:                    0
Rollback Index Location:  0
Release String:           'avbtool 1.3.0'
Descriptors:
    Hashtree descriptor:
      Version of dm-verity:  1
      Image Size:            800976896 bytes
      Tree Offset:           800976896
      Tree Size:             6311936 bytes
      Data Block Size:       4096 bytes
      Hash Block Size:       4096 bytes
      FEC num roots:         2
      FEC offset:            807288832
      FEC size:              6389760 bytes
      Hash Algorithm:        sha1
      Partition Name:        vendor
      Salt:                  b6497d667c35b54999e4eee6d8c57a3e606fe5bf5d1c2e4919e201e5fb624aa6
      Root Digest:           8740ffe9618882f976a71da4f743b19b3b9a01d4
      Flags:                 0
    Prop: com.android.build.vendor.os_version -> '15'
    Prop: com.android.build.vendor.fingerprint -> 'Ulefone/lineage_armol/armol:15/BP1A.250505.005/eng.armol:userdebug/test-keys'
```

## Kernel build warning

The successful BP1A vendor build emitted the Lineage warning that armol is
currently using a prebuilt kernel binary instead of a source-built kernel.

Classification:

`PREBUILT_KERNEL_WARNING_EXPECTED_FOR_CURRENT_BRINGUP`

This warning does not invalidate the vendor image or the current Slot-B vendor
investigation.

It remains technical debt for LieppOS full custom-kernel integration.

The eventual device tree should build the reconstructed Ulefone MT6878 kernel
from source instead of relying on the prebuilt-kernel path.

Warnings involving optional Wear/XR uses-libraries were also non-fatal for the
vendorimage target.

The duplicate BoardPlatform/ProductModel messages reported identical values
and therefore did not constitute a conflicting product configuration in this
build.

## Safety

- no ADB command was issued
- no fastboot command was issued
- no phone partition was written
- no slot state was modified
- current Slot A was not touched
- the mounted Slot-B vendor source was read only
- temporary copies were modified only inside the host temporary directory

## Next step

If the fixed built vendor differs from current Slot B only by the required
`init.insmod.mt6878.cfg`, it becomes a very narrow runtime candidate.

If additional logical differences exist, classify them before any replacement
of Slot-B vendor.

After content closure, the remaining preparation is AVB consistency and the
dynamic-partition write procedure for Slot B only.
