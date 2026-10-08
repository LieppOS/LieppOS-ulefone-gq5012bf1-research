# Axes 9–10: Android integration and significant native libraries

Audit date: 2026-10-07

## Method

`scripts/harvest-integration.py` records metadata only from the extracted stock partitions and compares basenames against the current `android_device_ulefone_gq5012bf1` and `vendor_ulefone_gq5012bf1` trees. It commits no proprietary bytes. Native-library consumers are ELF string-table witnesses, not a claim of a complete runtime call graph.

`scripts/build-integration.py` classifies the raw rows and joins every axis into `artifact-map.tsv`. There is no fallback to “covered”: the only `E` rows are explicit `UNMAPPED` rows.

## Android framework integration

`android-integration.tsv` contains 654 stock/current configuration artifacts (648 shipped plus 6 current-tree-only SELinux additions):

| Category | Rows |
|---|---:|
| init rc | 231 |
| permissions/features | 129 |
| audio config | 99 |
| VINTF | 75 |
| overlay/RRO | 43 |
| SELinux/policy contexts | 35 |
| thermal/power config | 16 |
| properties | 13 |
| media config | 6 |
| fstab | 4 |
| USB config | 2 |
| sensor config | 1 |

Coverage is A=127, B=428, C=99, D=0, E=0. A same-name counterpart exists in the current device/vendor trees for 261 rows; 387 are stock-only; 6 SELinux files are current-tree-only. `stock-only` is not automatically an RE gap: many are deliberately supplied through vendor extraction. Each row says whether the port should carry the stock file or author a replacement; current-only rows require compatibility/necessity review.

Ownership is concentrated in existing integration scopes (`ANDROID-INIT`, `VINTF-HAL-MANIFEST`, `VENDOR-SEPOLICY`, `VENDOR-PROPERTIES`, `PARTITION-OWNERSHIP`) and the relevant hardware scope for audio/camera/sensors/USB/power. No separate “one component per XML/RRO” taxonomy is justified.

## Significant userspace libraries

`userspace-libraries.tsv` groups 538 hardware-significant native library basenames across 32/64-bit paths:

| Domain | Rows |
|---|---:|
| Camera/ISP/3A | 269 |
| Audio/DSP | 95 |
| Graphics/GPU | 44 |
| Security/DRM | 42 |
| Sensors | 24 |
| Radio/IMS | 11 |
| Board glue | 9 |
| NVRAM/calibration | 8 |
| Charging/power | 7 |
| Bluetooth | 6 |
| GNSS | 6 |
| Thermal camera | 5 |
| Wi-Fi | 5 |
| NFC | 3 |
| Connectivity | 2 |
| Fingerprint | 1 |
| USB | 1 |

448 are device/vendor proprietary boundaries (`B`); 90 are generic/system helpers (`C`). Same-name payloads are already represented in the current vendor/device trees for 388 rows; 150 are stock-only. Kernel closure alone is explicitly **not** claimed sufficient for the 448 proprietary rows. They must either be retained as compatible blobs or replaced through a separately demonstrated userspace contract.

The five thermal-camera JNI libraries (`libAC020sdk`, `libadvirtemp`, `libadvirtempac020`, `libdualuvccamera020`, `libusbuvccamera020`) are owned by `THERMAL-RADIOMETRY`, not mistaken for Linux USB-driver gaps.

Mali/GPU userspace libraries are represented by `VENDOR-BLOB-HAL-INVENTORY`; that does not close the separate missing active Mali kernel/DT ownership scope.

## Dead/reference init evidence

Executable-presence is frozen into `raw-init-services.tsv`. Twenty-two non-trigger service declarations point to executables absent from all extracted stock partitions and are classified `D` rather than silently mapped as active. Notable families:

- five alternative fingerprint services (`btlfpserver`, legacy `fingerprintd`, Fptool, SwFingerprint and FocalTech) are absent; the image still carries their rc declarations;
- six legacy modem logger variants are absent;
- legacy `akmd8963`, `gnss_daemon`, `msensord`, `thermal_manager`, `permission_check` and several boot/debug helpers are absent;
- AOSP face-example and virtual-camera services are present but reference/example paths.

This is evidence of reference-board/vendor-template baggage, not evidence that six fingerprint implementations are active.

## Unified artifact map

`artifact-map.tsv` currently has 2,952 rows across axes 1–10. Its 10 `E` rows are exactly:

- three Mali kernel modules;
- three active Mali/GPU DT compatibles;
- two GPU VINTF families;
- two GPU init services.

All 10 converge on one confirmed missing ownership scope, not ten proposed components.
