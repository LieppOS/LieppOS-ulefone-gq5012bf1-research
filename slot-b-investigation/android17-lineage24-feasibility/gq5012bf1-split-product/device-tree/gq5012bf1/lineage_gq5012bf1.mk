# LineageOS 24 framework/userspace product for Ulefone GQ5012BF1.
# This first product intentionally does not build or replace the stock kernel,
# boot chain, vendor, vendor_dlkm, system_dlkm, or odm_dlkm.

DEVICE_PATH := device/ulefone/gq5012bf1

# core_64_bit must precede the product chain that reaches core_minimal.mk.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)
$(call inherit-product, $(DEVICE_PATH)/device.mk)
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

# Keep the normal Lineage phone package set in iteration 1. Optional apps and
# media are measured separately and are removed only if the split images fail
# their current extents; functionality is not stripped speculatively.

PRODUCT_NAME := lineage_gq5012bf1
PRODUCT_DEVICE := gq5012bf1
PRODUCT_BRAND := Ulefone
PRODUCT_MANUFACTURER := Ulefone
PRODUCT_MODEL := Armor 29 Pro
PRODUCT_GMS_CLIENTID_BASE := android-ulefone
