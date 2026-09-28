# Ulefone Armor 29 Pro / GQ5012BF1 framework-only board configuration.

DEVICE_PATH := device/ulefone/gq5012bf1

# Architecture. Keep the secondary ABI: the captured stock vendor contains 18
# ELF32 objects, including camera/TEE/fingerprint support libraries.
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-a
TARGET_CPU_VARIANT := generic
TARGET_CPU_ABI := arm64-v8a
TARGET_2ND_ARCH := arm
TARGET_2ND_ARCH_VARIANT := armv7-a-neon
TARGET_2ND_CPU_VARIANT := cortex-a15
TARGET_2ND_CPU_ABI := armeabi-v7a
TARGET_2ND_CPU_ABI2 := armeabi
TARGET_SUPPORTS_64_BIT_APPS := true
TARGET_SUPPORTS_32_BIT_APPS := true

TARGET_BOARD_PLATFORM := mt6878
TARGET_BOOTLOADER_BOARD_NAME := mt6878
TARGET_NO_BOOTLOADER := true
TARGET_NO_KERNEL := true
TARGET_NO_RADIOIMAGE := true

# These flags match the successful generic reference and retain its measured
# 209-file broad font set rather than applying an unreviewed language trim.
SMALLER_FONT_FOOTPRINT := true
MINIMAL_FONT_FOOTPRINT := true

# Real physical partition ownership; unlike the GSI, product and system_ext are
# not folded under /system.
TARGET_COPY_OUT_PRODUCT := product
TARGET_COPY_OUT_SYSTEM_EXT := system_ext
TARGET_COPY_OUT_VENDOR := vendor

TARGET_USERIMAGES_USE_EXT4 := true
TARGET_USERIMAGES_USE_F2FS := true
TARGET_USERIMAGES_SPARSE_EROFS_DISABLED := true
TARGET_USERIMAGES_SPARSE_EXT_DISABLED := true

BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_SYSTEM_EXTIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_PRODUCTIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_EROFS_COMPRESSOR := lz4hc,9
BOARD_EROFS_PCLUSTER_SIZE := 262144

# Exact currently allocated Slot-B extents. These are hard build limits; this
# tree does not resize super or alter logical metadata.
BOARD_SYSTEMIMAGE_PARTITION_SIZE := 665391104
BOARD_SYSTEM_EXTIMAGE_PARTITION_SIZE := 366891008
BOARD_PRODUCTIMAGE_PARTITION_SIZE := 337686528
BOARD_FLASH_BLOCK_SIZE := 262144

# Proven stock super geometry. Only the three framework-owned images are built
# in this host milestone; the existing vendor and DLKM images remain external.
BOARD_SUPER_PARTITION_SIZE := 9663676416
BOARD_SUPER_PARTITION_GROUPS := main
BOARD_MAIN_SIZE := 9661579264
BOARD_MAIN_PARTITION_LIST := \
    system \
    system_ext \
    product
BOARD_BUILD_SUPER_IMAGE_BY_DEFAULT := false

# AVB stays enabled with verity and FEC. A host test key signs build artifacts;
# it is not a phone acceptance key and these files are not flash packages.
BOARD_AVB_ENABLE := true
BOARD_AVB_ROLLBACK_INDEX := 0
BOARD_AVB_VBMETA_SYSTEM := system
BOARD_AVB_VBMETA_SYSTEM_KEY_PATH := external/avb/test/data/testkey_rsa2048.pem
BOARD_AVB_VBMETA_SYSTEM_ALGORITHM := SHA256_RSA2048
BOARD_AVB_VBMETA_SYSTEM_ROLLBACK_INDEX := $(PLATFORM_SECURITY_PATCH_TIMESTAMP)
BOARD_AVB_VBMETA_SYSTEM_ROLLBACK_INDEX_LOCATION := 1
BOARD_AVB_SYSTEM_ADD_HASHTREE_FOOTER_ARGS += --hash_algorithm sha256
BOARD_AVB_SYSTEM_EXT_ADD_HASHTREE_FOOTER_ARGS += --hash_algorithm sha256
BOARD_AVB_PRODUCT_ADD_HASHTREE_FOOTER_ARGS += --hash_algorithm sha256

# Stock/current B descriptor ownership: system belongs to vbmeta_system;
# product and system_ext descriptors belong to root vbmeta.
