# Port-readiness matrix

Audit date: 2026-10-07

This is a coverage/readiness assessment, not a build plan.

| Target | Assessment | Remaining RE/validation blockers |
|---|---|---|
| 1. Bootable custom kernel | **NEAR-READY / not runtime-proven** | BOOT-IMAGES exact-geometry boot test; DT source closure; GKI/KMI/vendor-module integration; add Mali KMD ownership. |
| 2. Full custom Android ROM | **MAPPED / integration incomplete** | VINTF, vendor properties, init, SELinux, blob extraction, camera/audio/radio/sensor/USB/power HAL integration. |
| 3. Daily-driver Android | **NOT YET VALIDATED** | Calls/data/IMS, camera, suspend, charging/thermal, fingerprint, NFC, sensors, GNSS, Wi-Fi/BT, DRM, OTA and recovery acceptance. |
| 4. Full hardware feature parity | **PROPRIETARY/PHYSICAL GATED** | Camera 3A/tuning, modem/RIL/IMS, SCP algorithms, DSP, fingerprint/TEE, radiometry/calibration, signed firmware and physical RF/thermal details. |
| 5. De-Googled LieppOS | **RE-MAPPED / product work remains** | No new hardware-RE gap; Google-free framework choices must retain compatible vendor HAL/blob contracts and decide DRM/attestation behavior. |
| 6. Stock-integrity secondary slot | **ARCHITECTURE MAPPED / safety validation open** | OTA/snapshot/FBE/shared metadata, boot-control rollback and recovery behavior must be tested without modifying the stock anchor slot. |
| 7. Future Linux slot | **KERNEL BASELINE STRONG / feature parity hard** | GPU KMD, display/input integration, modem userspace, SCP sensors, camera, DSP, charging policy and signed firmware remain major constraints. |

## Cross-cutting conclusions

- The port is no longer discovering major subsystems ad hoc: every audited axis has an owner or explicit generic/dead/proprietary classification.
- One source-actionable ownership hole remains: Mali GPU KMD/DT.
- Binary compatibility is still required for multiple daily-driver features; mapping a boundary does not make it open source.
- Physical/runtime validation is now the limiting factor for charging, battery, cooling, RF, microphones and end-to-end Android behavior.
