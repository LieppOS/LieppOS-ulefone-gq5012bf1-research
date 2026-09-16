# TIER3 Slot-B Provenance Recovery

## AVB private keys recovered

The exact private AVB keys used for the current Slot-B bring-up chain survive at:

`/mnt/SamsungSSD/TIER3/phase4/private/avb-bringup/`

Public-key SHA1 identities:

- root: `d6b1afef32b1fce5c47f537df3d7ec167ae2b469`
- system: `579a140d204d847f0c74332c73996baf1ed6a5fc`
- vendor: `664998c1c258771293715a829bd8caeae5d5626b`

These exactly match current B.

The Phase-4 generator created these dedicated RSA-2048 bring-up keys with
OpenSSL when absent. The boot chain key was deliberately retained from the
factory V15 boot-chain descriptor:

- boot: `9d808b0995768d0677fccb1efcddb7cf9e153d99`

## Current B provenance

The Phase-4 staging set:

`phase4/staging/complete-b-set/run-20260811T231651Z`

is byte-identical to current B for:

- boot
- init_boot
- vendor_boot
- dtbo
- system
- system_ext
- product
- vendor
- vendor_dlkm
- system_dlkm
- odm_dlkm

The full physical vbmeta partition hashes differ from the small staged vbmeta
files and require prefix/padding comparison before being classified as semantic
differences.

## Runtime-history discovery

Existing TIER3 Phase-5 reports show that Slot-B boot failure was already
investigated beyond the generic no-ADB symptom.

Recorded classifications include:

- `BOOTLOADER_SLOT_B_BL2_EXT_CRASH`
- later `BOOTLOADER_SLOT_B_FIRMWARE_CHAIN_MISSING`

Therefore the custom init_boot image is no longer the leading hypothesis until
the existing TIER3 BL2/firmware-chain evidence is fully reconciled with the
current device state.

No additional B boot, wipe, or partition modification should be performed until
that evidence is reviewed.

## Superseding TIER3 runtime chronology

The BL2 firmware-chain classification was an intermediate state, not the final
TIER3 runtime boundary.

TIER3 Phase 5 established this progression:

1. `lk_b` was initially all-zero, producing a preloader/BROM retry loop.
2. Provisioning `lk_b` advanced the failure to persistent `LK_CRASH(BL2_EXT)`.
3. Replacing `lk_b` with exact working same-device `lk_a` bytes produced the
   same `LK_CRASH(BL2_EXT)` signature, disproving LK generation mismatch as the
   sole cause.
4. Static BL2 analysis found 17 subordinate `_b` firmware partitions required by
   the selected-B path were zero-filled.
5. Those 17 partitions were provisioned from exact working-A same-device
   captures and read back 17/17 successfully.
6. A later controlled B attempt then exposed MediaTek USB PID `0e8d:201c`
   repeatedly, proving progress through Linux kernel entry and Android init USB
   configuration, but stable ADB and boot completion were never reached.

The latest TIER3 bounded diagnosis is therefore:

`KERNEL_INIT_USB_REACHED_ADB_OFFLINE_RESET_SEQUENCE`

not a remaining pre-kernel BL2 failure.

Before applying that August diagnosis to the current September state, the 17
subordinate live B firmware partitions must be re-hashed read-only and compared
to the exact TIER3 provisioned candidates.
