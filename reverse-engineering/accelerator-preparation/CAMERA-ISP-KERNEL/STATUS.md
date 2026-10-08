# CAMERA-ISP-KERNEL status — 2026-10-08

**DONE — scoped static normal-world kernel reconstruction (class A).**

All nineteen registered GQ5012BF1 camera/ISP kernel modules rebuild reproducibly from
public pinned source plus explicit device patches. Fresh-checkout B1/B2 acceptance covers:

* 2 970/2 971 exact functions; the remaining function is proven semantically equivalent;
* 2 474/2 474 exact data objects;
* 2 530/2 530 ABI records, including 1 792 import CRCs, 204 exports, 218 KCFI ids and
  316 `.modinfo` records;
* 978/978 identical section headers (955 exact contents, 19 build-ID-only and four
  declared residue rows); 71 990/71 991 exact relocations plus one proven moved byte load;
* all 225 participating intermediate objects reproducible; zero unresolved rows.

Seventeen modules have build-ID-only residue. `mtk_imgsys_cmdq` has one bounded
COMPILER_ONLY local symbol/string-table residue and `imgsensor` one bounded
PROVEN_SEMANTIC_EQUIVALENT codegen residue. Details and ledgers:
[RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md).

**Retained boundaries:** CCU/ISP firmware, CameraProvider/HAL, 3A, tuning, calibration
interpretation and image-quality algorithms remain proprietary under `CAMERA-HAL-ISP`
(PARTIAL). Sensor/EEPROM/VCM/OIS/flash/LDO scopes keep their existing owners.

**Runtime:** NOT TESTED. Probe, firmware boot, media topology, streaming, capture quality,
power/performance and failure recovery require the device acceptance plan in
[source-to-userspace-contract.md](source-to-userspace-contract.md).

Maintained recipe: `android_kernel_modules_camera_isp_ulefone_gq5012bf1` (local `main`,
not pushed); preserved bundle in `source/`.
