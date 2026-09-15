# Phase 3G-R blocker — local top-level vbmeta boot control

Status: **OPEN / C1-BLOCKING**

Classification: `PHASE3G_R_C0_LOCAL_VBMETA_BOOT_BLOCKED`.

C0 used exact stock B payloads and changed only top-level `vbmeta_b`. Its 27 raw descriptor records were stock-identical as a multiset, semantic difference count was zero, flags remained zero, and the image was signed with the same local AOSP RSA-2048 test key as Phase 3G.

The candidate was written and read back exactly. One B boot was attempted. No ADB or Fastboot transport appeared during the 300-second window or continued observation beyond eight minutes. Manual bootloader entry was required. No second B boot occurred.

Stock `vbmeta_b` was restored exactly. Final state is A current/active/bootable/successful, B bootable/not-successful, snapshot merge `none`; stock `vendor_boot_b` and `vendor_dlkm_b` remained exact throughout.

C1 is forbidden. TrustKernel module runtime was not tested. Resolution belongs to a separately reviewed AVB/Slot-B boot-chain diagnosis and may not use verification-disable, verity-disable, relocking, alternate bypasses, or the retired Phase-3G image.

Authoritative result: `kernel/phase4-tkcore-island-phase3g-r-C0-result.md`.
