# VINTF-HAL-MANIFEST — closure (2026-10-07, static)

Workspace component `Reverse Engineer - PARTIAL/VINTF-HAL-MANIFEST` → **DONE**.

## Scope

The device-side VINTF surface is reconciled at **instance level** (format,
package, version, interface, instance) between two sides:
* **stock:** 55 documents, namely `vendor/etc/vintf/manifest.xml`, 50
  fragments under `vendor/etc/vintf/manifest/`, and 4 ODM SIM-SKU manifests;
* **LieppOS:** the HAL set the device tree would assemble, which is
  `DEVICE_MANIFEST_FILE` + `ODM_MANIFEST_FILES` + the 41 stock fragment blobs
  that `proprietary-files.txt` installs (14 entries are `EXTRACT_ONLY`).

It also checks that every stock init service has its payload present.

Not in scope (integration): the build-time `assemble_vintf`/`checkvintf`
run, which needs a full Android checkout, and runtime service registration
under enforcing SELinux.

## Result

`scripts/vintf_reconcile.py` writes `evidence/vintf-instance-ledger.tsv`
(one row per instance) and `evidence/absent-service-payloads.tsv`.

| verdict | instances |
|---|---:|
| PRESENT in the LieppOS manifest set | 145 |
| ODM-SKU-VARIANT: only in `manifest_ss/tsts/qsqs` (slot3/4, SIM3/4, …); retail unit is DSDS | 48 |
| SOURCE-BUILT: the stock fragment is EXTRACT_ONLY, but an AOSP module in `PRODUCT_PACKAGES` ships the same instance (clearkey DRM, health, IR, sensors multihal, wifi) | 5 |
| **DROPPED** | **1** |

**The one real gap:** `aidl android.hardware.bluetooth.audio@3
IBluetoothAudioProviderFactory/default`.
* Stock declares it in `vendor/etc/vintf/manifest/bluetooth_audio.xml`.
* LieppOS ships the implementation (`android.hardware.bluetooth.audio-impl-mediatek.so`,
  loaded by the audio HAL), but the fragment is `EXTRACT_ONLY` and no
  source module replaces it.
* Without the fragment, framework BT-audio (A2DP/LE offload provider) lookup
  fails.
* Fix: drop `;EXTRACT_ONLY` from `vendor/etc/vintf/manifest/bluetooth_audio.xml`
  in `proprietary-files.txt` (integration).

**Absent stock payloads.** 12 init references resolve to 9 distinct
binaries; the other 3 references that looked absent are symlinks to
`.mt6878` binaries, so they are present. All 9 binaries are explained and
none blocks retail:

| class | services |
|---|---|
| alternate fingerprint BOM (MicroArray is fitted, see MICROARRAY-FP-TEE) | `btlfpserver`, `swfingerprint-hal-1.0`, `fptoolfingerprint-hal-2.0`, `vendor.focaltech.fps_hal` |
| factory/META boot mode only (`factory_init*.rc`, `meta_init*.rc`) | `spm_script`, `thermal_manager`, `permission_check` |
| 32-bit userspace absent (64-only device) | `boringssl_self_test32_vendor` |
| legacy GNSS daemon (MediaTek `mnld` is the GNSS engine) | `gnss_daemon` (common + meta rc) |

The service-ordering result (teed → KeyMint → Gatekeeper → Keystore2) and the
accounting policy are unchanged; see `notes/`.
