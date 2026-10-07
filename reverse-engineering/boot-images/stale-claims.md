# BOOT-IMAGES — stale claims corrected (2026-10-07)

| # | claim | verdict | correction |
|---|---|---|---|
| 1 | "Slot A carries a 2,555,526-byte LZ4 ramdisk; slot B a 2,343,040-byte gzip ramdisk" (listed as stock geometry) | **WRONG FRAMING** | Slot A `init_boot` is a **KernelSU-patched** image (`init.real`, `kernelsu.ko`) and fails the vbmeta_a hash. Only slot B (gzip) is stock and verifies. |
| 2 | vendor_boot slot A `recovery` fragment 33.5 MB as stock | **WRONG FRAMING** | It is the OrangeFox build (fails vbmeta_a). The stock recovery fragment is slot B, 4 714 551 B. |
| 3 | `init_boot.args` = `--header_version 4 … --cmdline ''` | **INCOMPLETE** | Stock (slot B) also carries `--os_version 15.0.0 --os_patch_level 2026-07`. Without them the repack differs. |
| 4 | "Re-derive geometry from the stock firmware directly when it is next unpacked" | **RESOLVED** | Geometry is re-derived from the device dumps by an exact round-trip (6/6 bodies identical). |
| 5 | "no custom boot/init_boot payload proven to boot" as a blocker | **RECLASSIFIED** | Kernel bring-up integration, not container understanding. |
