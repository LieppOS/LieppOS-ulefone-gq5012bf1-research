# Coverage verdict: NEAR-COMPLETE

Audit date: 2026-10-07

The 133-component list is not taxonomy-perfect and has one real coverage hole, but the device is now architecture-mapped across kernel, DT, physical hardware, Android integration, proprietary userspace, firmware, secure world and boot/storage. The only confirmed missing ownership scope is active Mali GPU KMD/DT.

## Measured headline

- Current components: **133** (DONE 94, PARTIAL 36, BLOCKED 3, TODO 0)
- Confirmed missing components: **1**
- Possible missing components: **0**
- Merge candidates: **4**
- Split candidates: **1**
- Stale/remove candidates: **2**
- Rename candidates: **1**
- Unified artifact rows: **2952**; E rows: **10**, all one GPU gap

### Kernel modules

- Total distinct shipped `.ko`: **457**
- Device-specific covered (A+B): **232** (A=66, B=166)
- Generic/no dedicated RE (C): **207**
- Dead/reference/debug baggage (D): **15**
- Unmapped (E): **3** — all active Mali KMD support

### Active device tree

- Distinct compatible rows: **580** across **930** compatible-bearing nodes
- Active/enabled compatible rows mapped: **571/574**
- Active E rows: **3** — the same Mali gap
- Active reference-board TDDI rows (D): **4**

### Vendor HAL/services

- Full harvested HAL/service rows: **525**
- Device-specific rows (C excluded): **337**
- Device-specific mapped: **333/337**; E=4, all GPU
- Generic/framework rows: **188**

### Firmware and secure world

- Firmware/calibration payloads mapped: **80/80** (signed 30, binary-only 41, source-available 8, device-internal 1)
- Secure-world surfaces represented: **13/13**

### PARTIAL triage

- A = **7** — Actionable / statically closeable
- B = **12** — Kernel/source closed; broader proprietary scope remains
- C = **8** — Proprietary boundary
- D = **4** — Hardware/runtime/teardown gated
- E = **0** — Stale/duplicate/wrong scope
- F = **5** — Broad umbrella/tracking scope

## Explicit answers

1. **Is the current list complete?** No: NEAR-COMPLETE. One active GPU ownership scope is missing.
2. **Exactly what is missing?** `MALI-GPU-KERNEL`, owning active Valhall KMD/MGM/protected-allocation modules, GPU DT and kernel-facing service ABI.
3. **How many new components are justified?** One missing ADD; one additional child is justified only by the camera split. Two newly named scopes after migration.
4. **Are there duplicates?** Yes, primarily the four per-module GZ children under GZ-TRANSPORT and the AW36518 v1/v2 folder pair.
5. **Which should merge?** GZ children→GZ-TRANSPORT; AW36518-V2→AW36518; USB3-FEASIBILITY→USB-TYPEC; VENDOR-ALL-MODULES-READY→INIT-INSMOD.
6. **Which should split?** CAMERA-HAL-ISP should split actionable CAMERA-ISP-KERNEL from proprietary HAL/3A/tuning.
7. **Are DONE components incorrectly scoped?** No automatic demotion is proven. DONE is static/named-scope only; several names/taxonomy entries need merge/remove/rename to avoid overbreadth.
8. **PARTIAL A–F?** A=7, B=12, C=8, D=4, E=0, F=5.
9. **Module classes?** device-specific covered=232, generic=207, dead/reference=15, unmapped=3.
10. **All active DT hardware represented?** 571/574 active compatible rows mapped; the three unmapped rows are one GPU scope. Physical inventory is 44/44 accounted, including absences/reference baggage.
11. **All meaningful vendor HAL/services represented?** 333/337 device-specific rows mapped; four E rows are the GPU scope.
12. **All firmware owners represented?** Yes, 80/80; source availability is classified separately.
13. **All TEE/security interfaces represented?** Yes, 13/13 normal-world/secure boundaries; signed TA source is not claimed.
14. **What remains worth static RE?** The ranked A-class list, camera ISP kernel split and Mali KMD; see PARTIAL-TRIAGE.md.
15. **What cannot become open parity without vendor/physical access?** Modem/RIL/IMS, camera 3A/tuning, SCP/DSP algorithms, thermal radiometry/calibration, fingerprint/TEE TAs, DRM/keys, per-unit calibration, signed firmware, RF/thermal/mechanical details.
16. **Best next 10?** YFT-DEVINFO, VINTF, vendor properties, FT3680, MT6375, DTB/DTBO, boot images, camera ISP kernel, Mali GPU kernel, vendor SELinux.
17. **Taxonomy changes?** 1 ADD, 1 SPLIT, 4 MERGE recommendations, 2 REMOVE, 1 RENAME and one metadata/status-text refresh.
18. **Corrected count if accepted?** **126** canonical components.
19. **Can subsystem discovery stop being ad hoc?** Yes for the current stock build: all ten axes now have measured inventories and explicit orphans. Re-run harvesters for any new stock build.
20. **Evidence?** 457 module rows, 580 compatible rows/930 nodes, 44 physical rows, 525 HAL/service rows, 80 firmware rows, 13 secure surfaces, 61 partition families, 654 Android-integration rows, 538 significant libraries and a 2,952-row unified artifact map.

## Best next 10 targets

1. **YFT-DEVINFO** — Quick static parity: one enum spelling plus probe/sysfs residual.
2. **VINTF-HAL-MANIFEST** — Generate final manifests/matrices and run VINTF checks.
3. **VENDOR-PROPERTIES** — Generate the property allowlist and validate contamination controls.
4. **FT3680-TOUCH** — Continue the bounded 40/68-function static residual.
5. **MT6375-CHARGER** — Close source/provider parity before runtime charging tests.
6. **DTB-DTBO** — Finish source-complete DTS and bootloader-mutation reconciliation.
7. **BOOT-IMAGES** — Produce exact-geometry custom images and validate Slot B boot.
8. **CAMERA-ISP-KERNEL (proposed split)** — Isolate actionable ISP kernel parity from proprietary HAL/3A.
9. **MALI-GPU-KERNEL (proposed add)** — Own the active Valhall KMD, MGM/protected allocator and three DT compatibles.
10. **VENDOR-SEPOLICY** — Build the device policy and close enforcing-runtime denials.

## Proposed resulting count

`133 + 1 ADD + 1 split child − 7 merged-away components − 2 removed absence components = 126`.

## Pack/manifest hygiene (separate from RE completeness)

Latest run: 4153/4153 manifest rows resolve; missing=0; malformed=0; stale hash/size=19; unregistered=408; duplicate paths=1.
The audit did not fix this unrelated drift. See notes/MANIFEST-HYGIENE.md.

## Commits created before this report

- `70871bf` — hardware/HAL/firmware/secure/boot axes and the single GPU gap
- `970711f` — all 133 canonical components and PARTIAL A–F triage
- `953b220` — Android integration, userspace libraries and unified artifact map

See [PROPOSED-CHANGES.md](PROPOSED-CHANGES.md), [PARTIAL-TRIAGE.md](PARTIAL-TRIAGE.md), [MISSING-COVERAGE.md](MISSING-COVERAGE.md) and [PORT-READINESS.md](PORT-READINESS.md).
