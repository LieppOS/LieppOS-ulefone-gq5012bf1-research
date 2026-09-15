# GQ5012BF1 TrustKernel Phase 3G-R C0 — stock-payload vbmeta control

Status: **HOST STATIC PASS / FRESH DEVICE GATE PASS / WRITE NOT YET AUTHORIZED**

## Purpose

C0 isolates one question: whether the device will boot Slot B when only top-level `vbmeta_b` is regenerated with the same local AOSP RSA-2048 test key used by Phase 3G while all described payloads remain stock.

C0 contains **zero TrustKernel module replacements** and changes no payload image other than top-level `vbmeta_b`.

## Output

- image: `workspace/phase4-tkcore-island/phase3g-r/c0/vbmeta_b.c0.img`
- bytes: `8388608`
- SHA-256: `46a6ec3b1572db72fb090e2fe68dbb0297a64b7dac825bf94ff488aff3640b18`
- stock `vbmeta_b` SHA-256: `e14e11e184950d487b31def17a349f4f161e34988825bf35d85fc9bd6c3bde93`
- algorithm: `SHA256_RSA2048`
- test-key PEM SHA-256: `f1d5765a2bdfb92fb08aee021107c7ac1a7a3f590dafd853771c85375ef0fbd7`
- embedded public-key SHA-1: `cdbb77177f731920bbe0a0f94f84d9038ae0617d`

Build input is exact restored stock `slot-b-investigation/device-dumps/vbmeta_b.img`. The command uses `avbtool 1.3.0 make_vbmeta_image`, `--include_descriptors_from_image` on that stock image, rollback index `0`, rollback-index location `0`, flags `0`, and stock-size padding.

## Header preservation

The following stock/C0 fields are equal:

- required libavb version: `1.0`;
- algorithm type: `SHA256_RSA2048`;
- descriptor bytes: `5680`;
- rollback index: `0`;
- rollback-index location: `0`;
- flags: `0`;
- release string: `avbtool 1.3.0`.

Authentication data, signature and embedded public-key material differ as required by the local signing key.

## Descriptor proof

Both images contain 27 descriptors. Each complete raw descriptor record, including all semantic values and embedded chain-key bytes, has an exact counterpart in the other image:

- raw descriptor multiset equal: **YES**;
- semantic differences: **0**;
- added descriptors: **0**;
- removed descriptors: **0**.

`avbtool` emitted the same descriptor records in a different order. Descriptor order is not a descriptor semantic field; the multiset and every raw record are exact. The committed per-record proof is:

`kernel/phase4-tkcore-island-phase3g-r-c0-descriptor-diff.tsv`

## Stock payload inputs

Locally retained B images used for host traversal remain stock:

| Image | SHA-256 |
|---|---|
| `boot_b.img` | `8648d0c9f071603ff601b49a656e1f52b5a6bae762772a4fd2cd8d73feb44927` |
| `vendor_boot_b.img` | `c8953d16b7a47976362aa23b53d0a08dde451f25cab4c552fa70c43e56ee0756` |
| `vendor_dlkm_b.img` | `fce7acfb64956126a03929f085050ab1b300272333e84abf27b9e708aaa40297` |
| `init_boot_b.img` | `c730a891bb93d48c41467ad00e749a9a7ae5d04695829082375974ea22b2b446` |
| `dtbo_b.img` | `9092967872d1362c45a18d62a83360b742eed58aafa4b0c15043ef159ae042d3` |
| `vbmeta_system_b.img` | `bd7f1bc3753a9914f325f1fc386883b780d507ec6f064e72942fd422e8cec358` |
| `vbmeta_vendor_b.img` | `42cfbc8fb1a987317cb82f9090e2c27a4f36af5fd52bd70c2d96591aad1ae794` |

No module file is rebuilt, extracted or replaced for C0.

## Host verification

`avbtool verify_image` proved before its bounded stop:

- C0 top-level SHA256_RSA2048 vbmeta structure/signature valid against the local key;
- `boot`, `vbmeta_system`, and `vbmeta_vendor` chain descriptors match the exact embedded stock child keys and rollback locations;
- stock `dtbo`, stock `init_boot`, and stock `vendor_boot` hashes resolve exactly.

Complete recursive traversal is **not claimed**. It stops at absent local `odm_dlkm.img`, an unchanged stock dynamic child that was not retained. Stock `vendor_dlkm_b.img` was independently verified by `avbtool` with RC 0.

Evidence:

- `workspace/phase4-tkcore-island/phase3g-r/c0/c0-build-validation.json`
- `workspace/phase4-tkcore-island/phase3g-r/c0/c0-bounded-traversal.txt`
- `workspace/phase4-tkcore-island/phase3g-r/c0/stock-vendor_dlkm-verify.txt`
- `workspace/phase4-tkcore-island/phase3g-r/c0/{stock,c0}-vbmeta-info.txt`

## Fresh read-only device gate

The authorized serial `5012BF3010001335` is the only connected target. Fresh Android and bootloader checks prove:

- A current, active-next-boot, bootable and successful;
- B bootable and not successful;
- snapshot merge `none`;
- bootloader product `k6878v1_64`, `unlocked=yes`, `secure=no`;
- exact restored stock hashes and sizes for `boot_b`, `vendor_boot_b`, `vendor_dlkm_b`, `init_boot_b`, `dtbo_b`, `vbmeta_b`, `vbmeta_system_b`, and `vbmeta_vendor_b`.

Evidence:

- `workspace/phase4-tkcore-island/phase3g-r/c0/device-before/android-readonly-gate.txt`
- `workspace/phase4-tkcore-island/phase3g-r/c0/device-before/b-payload-hashes.tsv`
- `workspace/phase4-tkcore-island/phase3g-r/c0/device-before/fastboot-readonly-gate.txt`

## Device boundary

No Phase-3G-R device write has occurred. C0 may write only `vbmeta_b` after fresh explicit authorization for that one write, one B boot attempt, and exact stock-vbmeta restoration afterward whether the control passes or fails.
