# Proposed taxonomy changes



Audit date: 2026-10-07



Recommendations only. No component folder/status was moved by this audit.



### PC-001

- **type:** ADD
- **component(s):** MALI-GPU-KERNEL
- **reason:** One active board-specific kernel/DT ownership scope is absent.
- **evidence:** 3 E modules + 3 E DT compatibles + 2 E VINTF families + 2 E init services.
- **risk:** Medium: do not absorb proprietary userspace/firmware into a source-closure claim.
- **suggested action:** Create only after review; start PARTIAL/A and own KMD/DT ABI.

### PC-002

- **type:** SPLIT
- **component(s):** CAMERA-HAL-ISP → CAMERA-HAL-ISP + CAMERA-ISP-KERNEL
- **reason:** One PARTIAL mixes statically actionable ISP modules with permanently proprietary HAL/3A/tuning/CCU.
- **evidence:** Component README and camera axis identify mixed kernel parity and proprietary userspace.
- **risk:** Medium: module ownership and links must move without implying open 3A parity.
- **suggested action:** Create CAMERA-ISP-KERNEL (PARTIAL/A); narrow CAMERA-HAL-ISP to proprietary userspace boundary (C).

### PC-003

- **type:** MERGE
- **component(s):** GZ-IPC-MOD, GZ-MAIN-MOD, GZ-TRUSTY-MOD, GZ-TZ-SYSTEM → GZ-TRANSPORT
- **reason:** Four per-module children share one GenieZone transport completion criterion and the parent already summarizes them.
- **evidence:** Each child README cross-links GZ-TRANSPORT; all are DONE exact-source transport pieces.
- **risk:** Low: preserve per-module parity reports under subdirectories.
- **suggested action:** Use GZ-TRANSPORT as survivor; migrate evidence/manifest paths, reducing five components to one.

### PC-004

- **type:** MERGE
- **component(s):** AW36518-V2-FLASH → AW36518-FLASH
- **reason:** Two shipped source variants implement one AW36518-family physical ownership boundary.
- **evidence:** Sibling READMEs explicitly compare v1/v2 topology and parity.
- **risk:** Low: preserve both module/source variants as subreports.
- **suggested action:** Keep AW36518-FLASH and add v1/v2 subsections.

### PC-005

- **type:** MERGE
- **component(s):** USB3-FEASIBILITY → USB-TYPEC
- **reason:** Resolved-negative capability study is a board fact, not a continuing component.
- **evidence:** Stock boot log proves zero USB3 ports; USB-TYPEC already owns board USB capability.
- **risk:** Low: preserve the negative proof prominently.
- **suggested action:** Move report into USB-TYPEC and retire the standalone component.

### PC-006

- **type:** MERGE
- **component(s):** VENDOR-ALL-MODULES-READY → INIT-INSMOD
- **reason:** A single init property lifecycle is part of the module-loader/init ownership boundary.
- **evidence:** README proves sole setter/consumer ordering around insmod_sh.
- **risk:** Low.
- **suggested action:** Move the property timeline into INIT-INSMOD.

### PC-007

- **type:** REMOVE
- **component(s):** ESIM-EUICC-ABSENCE
- **reason:** Proven absence is a finding, not an ongoing RE ownership scope.
- **evidence:** No fitted eUICC in hardware/software inventory.
- **risk:** Low: losing the negative conclusion if not migrated.
- **suggested action:** Preserve in hardware.tsv/MISSING-COVERAGE.md, then retire folder.

### PC-008

- **type:** REMOVE
- **component(s):** WIRELESS-CHARGING-ABSENCE
- **reason:** Proven absence is a finding, not an ongoing component.
- **evidence:** No wireless charging path in DT/modules/init/hardware evidence.
- **risk:** Low: preserve distinction from wired reverse charging.
- **suggested action:** Preserve in hardware/power reports, then retire folder.

### PC-009

- **type:** RENAME
- **component(s):** RT5133-POWER-IC → RT5133-CAMERA-LDO-INTEGRATION
- **reason:** Current name preserves the superseded 4-phase-buck ambiguity.
- **evidence:** Newest runtime evidence has rt5133 bound at I2C 5-0018 as a camera-sensor LDO/power path; exact die/rails remain hardware-gated.
- **risk:** Medium: update every manifest/link without reopening proven static work.
- **suggested action:** Rename only; keep DONE as named static scope and preserve the hardware-checkout boundary.

### PC-010

- **type:** STATUS
- **component(s):** OEM-KERNEL-MODULES and VENDOR-DLKM metadata
- **reason:** Their prose still cites a 471-module set while the authoritative union is 457.
- **evidence:** kernel-modules.tsv reconciles all module locations and metadata to 457 distinct .ko names.
- **risk:** Low; no directory status move.
- **suggested action:** Refresh counts/scope prose; remain PARTIAL/F umbrella trackers.



## Net component count if accepted



Current 133 + one ADD + one split-created child − four GZ children − one AW36518 variant − one USB3 study − one init-property component − two absence components = **126 canonical components**.



The rename and metadata/status-text refresh do not change the count. There are **two newly named scopes** after migration: one genuinely missing ADD and one split-created kernel child.
