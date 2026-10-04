# Boot control (storage-facing summary)

This summarises the existing Slot-B research (`slot-b-investigation/slot-control-analysis/boot-service-real-method-analysis.md`, binary sha256 `f247dde9…`) and does not repeat it. No boot-control state was written.

| item | GQ5012BF1 |
|---|---|
| HAL | AIDL `android.hardware.boot.IBootControl/default`, `/vendor/bin/hw/android.hardware.boot-service.mtk` (service `vendor.boot-default`, `class early_hal`, root) |
| slot metadata | standard Android `bootloader_control`, 32 bytes at **`/misc` + 0x800** (`/misc` resolved from fstab, `/dev/block/by-name/misc` = `sdc1`), CRC32 over 28 bytes, magic `BCAB`, version 1, `nb_slot = 2` |
| active | highest `priority`. `setActiveBootSlot` sets priority 15 and tries 6, and caps the other slot at 14 |
| successful | `successful_boot && tries_remaining`. `markBootSuccessful` sets successful=1, tries=1, then clears the MTK AVB "conversion flag" byte at BCB `+0x14` |
| unbootable | `setSlotAsUnbootable`: successful=0, tries=0 |
| retry count | `tries_remaining` (6 on activation) |
| UFS physical boot region | after the BCB write, `SetBootRegionSlot(slot)` calls `libmtk_bsg.so` `ioctrl_w_attr("/dev/ufs-bsg0", idn=bBootLunEn, value = slot+1)`. This selects **Boot LU A (LU0) or B (LU1)**, i.e. which preloader copy BootROM loads. An eMMC `mmcblk0` boot-partition fallback exists in the same function |
| kernel interface | **GKI** UFS BSG (`CONFIG_SCSI_UFS_BSG=y`, `/dev/ufs-bsg0`, UPIU QUERY WRITE ATTR). No MTK kernel module is involved |
| Virtual A/B merge status | `get/setSnapshotMergeStatus` in the misc virtual-A/B message area (initialised by the HAL) |
| captured state (existing) | slot A priority 7 / tries 1 / successful 1; slot B priority 6 / tries 4 / successful 0 |
