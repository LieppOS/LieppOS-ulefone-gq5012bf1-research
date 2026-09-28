# Product inheritance and partition architecture

## Inheritance order

```make
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)
$(call inherit-product, device/ulefone/gq5012bf1/device.mk)
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)
```

This is a standard full Lineage phone product. It does **not** inherit
`device/generic/common/gsi_arm64.mk` or `gsi_release.mk`, so `BUILDING_GSI` and
`BUILDING_LINEAGE_GSI` are empty.

## Physical split

Board configuration sets:

```text
TARGET_COPY_OUT_SYSTEM_EXT=system_ext
TARGET_COPY_OUT_PRODUCT=product
BOARD_USES_SYSTEM_EXTIMAGE=true
BOARD_USES_PRODUCTIMAGE=true
PRODUCT_BUILD_SYSTEM_IMAGE=true
PRODUCT_BUILD_SYSTEM_EXT_IMAGE=true
PRODUCT_BUILD_PRODUCT_IMAGE=true
```

The build emitted all three images. Final installed paths begin `/system`,
`/system_ext`, and `/product`; there are no `/system/system_ext` or
`/system/product` folded roots. `PARTITION-PACKAGE-MAP.tsv` accounts for every
installed-file JSON entry under its final logical owner.

## Product identity

```text
PRODUCT_NAME=lineage_gq5012bf1
PRODUCT_DEVICE=gq5012bf1
PRODUCT_BRAND=Ulefone
PRODUCT_MANUFACTURER=Ulefone
PRODUCT_MODEL=Armor 29 Pro
Android=17
SDK=37
Lineage=24.0
security patch=2026-09-01
build ID=CP2A.260605.016
```

No Android 15→16 property shim and no insecure-adb property is inherited.

## External unchanged partitions

The first product intentionally sets build flags false for boot, init_boot,
vendor_boot, dtbo, vendor, vendor_dlkm, system_dlkm, odm_dlkm, userdata, cache,
and super. It therefore exercises the Android 17 framework/userspace build
without producing replacements for the current Ulefone kernel/vendor stack.

The dynamic-partition list contains the three images being budgeted. The stock
super geometry is documented, but `BOARD_BUILD_SUPER_IMAGE_BY_DEFAULT=false`
and no super image is produced or modified.
