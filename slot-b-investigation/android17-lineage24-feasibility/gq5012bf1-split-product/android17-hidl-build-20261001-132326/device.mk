# Minimal Android 17 framework/userspace integration for GQ5012BF1.

DEVICE_PATH := device/ulefone/gq5012bf1

$(call inherit-product, $(SRC_TARGET_DIR)/product/virtual_ab_ota.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/emulated_storage.mk)

PRODUCT_USE_DYNAMIC_PARTITIONS := true
PRODUCT_FULL_TREBLE_OVERRIDE := true
PRODUCT_ENFORCE_VINTF_MANIFEST := true
PRODUCT_SHIPPING_API_LEVEL := 35

# Required declarations for the exact vendor-specific and non-standard
# instances in the captured stock V15 vendor + DSDS manifest. This matrix has
# no optional entries and does not relax the platform FCM.
DEVICE_FRAMEWORK_COMPATIBILITY_MATRIX_FILE += \
    $(DEVICE_PATH)/vintf/framework_compatibility_matrix.xml

# Stock vendor reports ro.vndk.version=34. ELF closure found no dependency that
# exists only in VNDK 31/32/33; Android 17 no longer has a current platform VNDK.
PRODUCT_EXTRA_VNDK_VERSIONS := 34

PRODUCT_SOONG_NAMESPACES += $(DEVICE_PATH)

# Host-only userspace milestone: preserve the existing Ulefone kernel/vendor
# stack by not emitting replacement images for it.
PRODUCT_BUILD_BOOT_IMAGE := false
PRODUCT_BUILD_INIT_BOOT_IMAGE := false
PRODUCT_BUILD_VENDOR_BOOT_IMAGE := false
PRODUCT_BUILD_VENDOR_IMAGE := false
PRODUCT_BUILD_VENDOR_DLKM_IMAGE := false
PRODUCT_BUILD_SYSTEM_DLKM_IMAGE := false
PRODUCT_BUILD_ODM_DLKM_IMAGE := false
PRODUCT_BUILD_DTBO_IMAGE := false
PRODUCT_BUILD_USERDATA_IMAGE := false
PRODUCT_BUILD_CACHE_IMAGE := false
PRODUCT_BUILD_SUPER_PARTITION := false
PRODUCT_BUILD_SUPER_EMPTY_IMAGE := false
PRODUCT_BUILD_PVMFW_IMAGE := false

# Build framework-owned read-only images and their AVB metadata only.
PRODUCT_BUILD_SYSTEM_IMAGE := true
PRODUCT_BUILD_SYSTEM_EXT_IMAGE := true
PRODUCT_BUILD_PRODUCT_IMAGE := true

# No ro.product.first_api_level override: the build system generates that
# property from PRODUCT_SHIPPING_API_LEVEL into the vendor-side property set,
# which on this device is the untouched stock vendor build.prop (it already
# declares ro.product.first_api_level=35). The secondary ABI required by the
# captured ELF32 vendor objects is configured in BoardConfig.mk.


# Android 17 / FCM 8:
# The Ulefone vendor image still exposes legacy HIDL HALs.
# Keep the legacy HIDL runtime available even though this product
# ships with PRODUCT_SHIPPING_API_LEVEL := 35.
PRODUCT_PACKAGES += \
    hwservicemanager \
    android.hidl.allocator@1.0-service \
    android.hidl.memory@1.0-impl
