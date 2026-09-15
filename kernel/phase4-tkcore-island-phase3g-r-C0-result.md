# GQ5012BF1 TrustKernel Phase 3G-R — C0 result

Classification: **PHASE3G_R_C0_LOCAL_VBMETA_BOOT_BLOCKED**

## Control definition

C0 changed only top-level `vbmeta_b`. All payloads, including `vendor_boot_b` and `vendor_dlkm_b`, were exact stock. The C0 vbmeta contained the exact stock 27-descriptor semantic multiset, flags `0`, rollback index `0`, and was signed with the same local AOSP RSA-2048 test key used in Phase 3G.

- C0 vbmeta SHA-256: `46a6ec3b1572db72fb090e2fe68dbb0297a64b7dac825bf94ff488aff3640b18`
- descriptor semantic differences: `0`
- changed module payloads: `0`
- verification disabled: no
- verity disabled: no

## Authorized write

Fresh explicit authorization covered one `vbmeta_b` write, one B boot attempt, return to A, and exact stock-vbmeta restoration whether the control passed or failed.

The bootloader Fastboot write reported `Writing 'vbmeta_b' OKAY`. A-side readback then proved:

- `vbmeta_b` exactly C0 candidate;
- `vendor_boot_b` still exact stock;
- `vendor_dlkm_b` still exact stock.

Evidence:

- `workspace/phase4-tkcore-island/phase3g-r/c0/device-write/c0-vbmeta-flash.txt`
- `workspace/phase4-tkcore-island/phase3g-r/c0/device-write/c0-post-write-hashes.tsv`

## Single B boot

B was selected and bootloader metadata relatched. Immediately before boot:

- `current-slot: b`;
- `slot-unbootable:b: no`.

Exactly one `fastboot reboot` was issued. The device produced neither ADB nor Fastboot transport during the 300-second bounded window. Continued observation exceeded eight minutes with no Android, Fastboot, or MediaTek USB enumeration. The phone remained at a logo/warning and required the user to enter normal bootloader mode manually.

Consequently:

- C0 B boot: **FAIL**;
- authoritative `_b` Android identity: **not proven**;
- local top-level test key accepted: **NO** for this boot-chain control;
- C0 boot attempts: `1`;
- B retries: `0`.

Evidence: `workspace/phase4-tkcore-island/phase3g-r/c0/device-write/c0-single-boot.txt`.

## Restoration and final state

Manual recovery reached normal bootloader Fastboot with B current, B bootable/not-successful, and A bootable. A was selected and relatched before restoring stock `vbmeta_b`.

Final A-side proof:

- stock `vbmeta_b`: `e14e11e184950d487b31def17a349f4f161e34988825bf35d85fc9bd6c3bde93` — exact;
- stock `vendor_boot_b`: `c8953d16b7a47976362aa23b53d0a08dde451f25cab4c552fa70c43e56ee0756` — exact;
- stock `vendor_dlkm_b`: `fce7acfb64956126a03929f085050ab1b300272333e84abf27b9e708aaa40297` — exact;
- A current and active-next-boot;
- A bootable and successful;
- B bootable and not successful;
- snapshot merge `none`.

Evidence:

- `workspace/phase4-tkcore-island/phase3g-r/c0/device-write/c0-stock-vbmeta-restore.txt`
- `workspace/phase4-tkcore-island/phase3g-r/c0/device-write/c0-final-restoration-state.txt`

## Interpretation and stop

This stock-payload control isolates the failure from TrustKernel module replacements. The local test-key-signed top-level vbmeta strategy is not accepted by the observed B boot chain under the tested device state, despite bootloader Fastboot reporting `unlocked=yes`, `secure=no`.

C1 is **forbidden and not attempted**. No alternative AVB bypass, verification disable, verity disable, second B boot, module test, KeyMint/Gatekeeper/FBE/fingerprint/Widevine test or additional partition write is permitted in Phase 3G-R.

Next work is AVB / Slot-B boot-chain diagnosis under a separately reviewed phase.
