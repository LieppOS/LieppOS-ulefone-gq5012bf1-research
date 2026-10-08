# CAMERA-HAL-ISP / CAMERA-ISP-KERNEL ownership split

The initial 2026-10-08 preparation registered the child as PARTIAL. Subsequent
reconstruction closes **CAMERA-ISP-KERNEL as DONE** for all nineteen normal-world kernel
modules: pinned source, explicit patches, complete parity ledgers and independent B1/B2.
Parent **CAMERA-HAL-ISP stays PARTIAL**. See the
[reconstruction report](../accelerator-preparation/CAMERA-ISP-KERNEL/RECONSTRUCTION-REPORT.md).

## Current authoritative scopes

- **CAMERA-ISP-KERNEL:** the exact 19-module [primary ownership ledger](../accelerator-preparation/CAMERA-ISP-KERNEL/stock-modules.tsv), ISP/SENINF/CCD/CCU/AIE/DPE/PDA/VMM/framework/C2PS kernel DT and observable ABI. [Claude handoff](../accelerator-preparation/CAMERA-ISP-KERNEL/CLAUDE-HANDOFF.md).
- **CAMERA-HAL-ISP:** proprietary CameraProvider/HAL, 3A, tuning, image algorithms, calibration interpretation, retained ISP/CCU payloads and ROM integration. Kernel inventory references in older parent notes are historical, not duplicate current primary ownership.
- Closed sensor translation units, EEPROM/VCM/OIS/flash/rails retain their existing named DONE scopes. A whole imgsensor module has one primary framework owner; named sensor TUs remain closed subscopes, not a second whole-module owner.
- Generic clocks/SMI/IOMMU/bus/PMIC providers are dependencies, not camera HAL implementation or newly fabricated source parity.
- APUSYS/MDLA/MVPU/APU-RPMsg accelerator declarations now belong to APUSYS-NPU-KERNEL, not camera consumers. AIE/FD camera hardware stays the ISP child.

## Evidence preserved

Existing sources, build recipes, stock operands and all camera history stay in their original paths, including `kernel-isp-imgsys/`, the grafted private mtkcam tree and old pack evidence. The child now preserves its public-source reconstruction recipe, explicit source patches
and full acceptance evidence, but no duplicated proprietary firmware or HAL payload. Ownership was transferred explicitly through the canonical coverage policy and preparation ledgers.

The initial sixteen function/data proof pairs are historical evidence, not the current
acceptance ceiling. All nineteen modules now have independent complete acceptance;
PDA/VMM match unmodified public source. The current ledgers cover 2,971 functions,
2,474 data objects, 2,530 ABI records, 978 sections and 71,991 relocations with zero
unresolved. The one imgsensor function/moved byte-load and the cmdq private-name residues
are bounded and proved in the reconstruction report. Do not restart the closed subscopes.

[Roadmap](../accelerator-re-roadmap.md). Whole proprietary camera algorithms and later phone streaming/quality validation are not kernel-source DONE requirements, and source parity does not prove a finished runtime camera feature.
