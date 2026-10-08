# CAMERA-HAL-ISP / CAMERA-ISP-KERNEL ownership split

Authorized accelerator preparation, 2026-10-08. Parent **CAMERA-HAL-ISP stays PARTIAL**. New kernel child **CAMERA-ISP-KERNEL starts PARTIAL**. No reconstruction, destructive move or deletion was performed.

## Current authoritative scopes

- **CAMERA-ISP-KERNEL:** the exact 19-module [primary ownership ledger](../accelerator-preparation/CAMERA-ISP-KERNEL/stock-modules.tsv), ISP/SENINF/CCD/CCU/AIE/DPE/PDA/VMM/framework/C2PS kernel DT and observable ABI. [Claude handoff](../accelerator-preparation/CAMERA-ISP-KERNEL/CLAUDE-HANDOFF.md).
- **CAMERA-HAL-ISP:** proprietary CameraProvider/HAL, 3A, tuning, image algorithms, calibration interpretation, retained ISP/CCU payloads and ROM integration. Kernel inventory references in older parent notes are historical, not duplicate current primary ownership.
- Closed sensor translation units, EEPROM/VCM/OIS/flash/rails retain their existing named DONE scopes. A whole imgsensor module has one primary framework owner; named sensor TUs remain closed subscopes, not a second whole-module owner.
- Generic clocks/SMI/IOMMU/bus/PMIC providers are dependencies, not camera HAL implementation or newly fabricated source parity.
- APUSYS/MDLA/MVPU/APU-RPMsg accelerator declarations now belong to APUSYS-NPU-KERNEL, not camera consumers. AIE/FD camera hardware stays the ISP child.

## Evidence preserved

Existing sources, build recipes, stock operands and all camera history stay in their original paths, including `kernel-isp-imgsys/`, the grafted private mtkcam tree and old pack evidence. The child has inventories and links, not duplicated private source or firmware. Ownership was transferred explicitly through the canonical coverage policy and preparation ledgers.

Sixteen owned modules have published function/data proof pairs. These include the 1220-function camsys report and imgsensor's one documented semantic residual. Do not repeat this reconstruction or downgrade the measured axes. PDA and VMM regulator/notifier lack those proof pairs; full per-module CRC/KCFI/relocation/symbol/string/.modinfo/vermagic/B1-B2 and observable DT/ABI acceptance must be certified independently. No new parity was measured by this preparation.

[Roadmap](../accelerator-re-roadmap.md). Whole proprietary camera algorithms and later phone streaming/quality validation are not kernel-source DONE requirements, and source parity does not prove a finished runtime camera feature.
