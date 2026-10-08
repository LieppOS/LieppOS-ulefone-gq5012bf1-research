# LieppOS development readiness

Snapshot: **2026-10-08**, source HEAD `c8de6a1`. Actual workspace directory status is authoritative; scope registration is not kernel reconstruction.

| Target | Assessment | Remaining work |
|---|---|---|
| Custom GKI/kernel | Static baseline strong; custom boot unproved | Preserve SYSTEM-DLKM 60/60 baseline, exact containers and KMI; close accelerator/source/DT ABI and validate actual boot later. |
| Full custom ROM | Integration incomplete | Preserve external 24afa6b vendor.prop and bluetooth_audio.xml fixes; verify emitted properties, VINTF, init, enforcing SELinux and real HAL registration. |
| Daily driver | NOT PROVEN | Actual boot, radio/IMS, camera/audio, connectivity, sensors, fingerprint/NFC, suspend, charging/thermal, OTA/recovery acceptance remains. |
| Hardware parity | Proprietary/physical/runtime gated | Retain CSF/APU/VCP/CCU/SCP/DSP/modem images, 3A/PQ/tuning, RIL/IMS, TAs and calibration; static preparation proves no accelerator execution. |
| Google-free LieppOS | Product integration work | Remove/replace Google services while retaining vendor contracts; decide DRM/attestation/app compatibility. |
| Stock-integrity secondary slot | Stock B anchor verified | Preserve B and shared userdata/FBE/metadata/rollback/snapshot state; never overwrite anchor for experimental tests. |
| Future Linux slot | Source-actionable baseline, feature parity uncertain | Accelerator source/ABI, remote firmware, Linux userspace replacements, audio/sensors/modem/display and power policy remain. |

## Existing closures preserved

- **SYSTEM-DLKM (DONE)**: 60/60 stock ELF bodies incl. build-id reproduced; appended signing key differs. Custom-kernel/KMI packaging and boot remain integration.. [Research](../system-dlkm/STATUS.md).
- **BOOT-IMAGES (DONE)**: Six stock container round-trips byte-identical; Slot B stock verified, Slot A modified. Custom-kernel boot/recovery acceptance is NOT closed.. [Research](../boot-images/STATUS.md).
- **VENDOR-PROPERTIES (DONE)**: 747-key ledger closed; external 24afa6b installs 327 vendor keys with 16 exclusions/one EGL rewrite from the original 343-key gap. Verify emitted-image/generated definitions and SELinux/runtime; not applied by audit.. [Research](../vendor-properties/STATUS.md).
- **VINTF-HAL-MANIFEST (DONE)**: 199 instances reconciled: 146 present, 48 SKU-only, 5 source-built, 0 dropped after external 24afa6b includes bluetooth_audio.xml. checkvintf/SELinux/HAL runtime remain; not applied by audit.. [Research](../vintf-hal-manifest/STATUS.md).
- **PARTITION-OWNERSHIP (DONE)**: 61 partition groups and rollback locations 0/2/3/4 mapped. Private payload semantics and destructive rollback/OTA tests outside scope.. [Research](../partition-ownership/STATUS.md).
- **USB-CHARGER-INTEGRATION (DONE)**: Framework/class/type-detect module parity closed; 120 W/reverse-power negotiation and safety transitions NOT runtime-validated.. [Research](../usb-charger-integration/STATUS.md).
- **INTERNAL-THERMAL-USB (DONE)**: Kernel USB/UVC/power contract closed; viewer/command/radiometry and runtime thermal-camera acceptance remain separate scopes.. [Research](../thermal-camera/internal-usb/STATUS.md).

Do not force RT5133 binding; the observed failure releases GPIO1 for the working WL2864C camera rails. [Correction](notes/RT5133-CORRECTION.md). Property installation, build success and component DONE never replace runtime acceptance.
