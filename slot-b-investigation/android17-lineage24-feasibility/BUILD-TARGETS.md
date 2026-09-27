# Generic Android 17 build targets

## Target discovery

**PROVEN from source:** old Treble-script names are absent:

```text
lineage_arm64           count 0
lineage_arm64_bvN       count 0
lineage_arm64_bvS       count 0
lineage_arm64_bgN       count 0
lineage_arm64_bgS       count 0
```

Official Lineage 24 defines `lineage_gsi_arm64` in
`vendor/lineage/build/target/product/lineage_gsi_arm64.mk`. Available generic
Lineage products include arm/arm64/x86/x86_64 and car/TV variants. The phone
candidate is:

```sh
source build/envsetup.sh
lunch lineage_gsi_arm64 cp2a userdebug
```

Android 17 rejects the old two-field `lineage_gsi_arm64-userdebug` syntax and
requires product, release, variant.

## Product character

- ARM64 primary ABI plus ARM 32-bit secondary ABI.
- Official Lineage base, vanilla/no GApps. No Google package set is inherited.
- `full_base_telephony` plus Lineage `common_full_phone`.
- 826 unique configured packages in the inspected userdebug graph.
- `PRODUCT_USE_DYNAMIC_PARTITIONS=true` and dynamic image sizing.
- Generic target uses ext4 by default.
- EROFS is source-supported through `GSI_FILE_SYSTEM_TYPE=erofs`; it must be an
  explicit controlled build variant, not an assumption.

## Critical layout fact

**PROVEN:** this GSI does **not** build independent product and system_ext
partitions:

```text
TARGET_COPY_OUT_PRODUCT=system/product
TARGET_COPY_OUT_SYSTEM_EXT=system/system_ext
```

`gsi_release.mk` sets `BOARD_USES_PRODUCTIMAGE=false` and
`BOARD_USES_SYSTEM_EXTIMAGE=false`; their contents are folded into system.
This is appropriate for a DSU/GSI proof but incompatible with the current B
three-extent layout without a device-specific product configuration.

The GSI target also installs compatibility packages for shipping API 29, 33 and
34, VNDK snapshots 31–34, old HIDL allocator/memory services, wificond, legacy
OMX, and GSI SELinux debug policy. These explain some payload and are not all
optional while the Android-14-generation vendor is retained.

## Production direction

**INFERRED:** use `lineage_gsi_arm64` only to validate Android 17 framework ↔
current vendor/kernel behavior (preferably through DSU). The flashable Slot-B
candidate must become `lineage_gq5012bf1` with separate EROFS system,
system_ext and product images sized to the existing extents.
