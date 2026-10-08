# APUSYS-NPU-KERNEL — PARTIAL preparation

Status: PARTIAL

- **Subsystem:** Accelerators / APUSYS/NPU
- **Hardware identity:** MT6878 APU RV complex at apusys-rv@190e1000, apu-top-3@1c000000, APUMMU, APU IOMMU banks and MDLA/MVPU/EDMA/RPMsg channel declarations. The monolithic apusys.ko contains multiple IP generations: alias presence does not mean every generation is enabled. Separate board DT instances from dormant code.
- **Stock artifact:** `apu_top.ko`, `apusys.ko`
- **Interfaces:** apu_top power/DVFS callbacks; apusys middleware command submission, buffer/shared-memory management, APUMMU/reviser translation, RPMsg/mailbox/interrupt transport, EDMA/MDLA/MVPU completion and recovery. Extract APUSYS ioctl command numbers and native/compat layouts from source witnesses and compare stock switch paths. Recover ownership of each buffer through allocation, map, submit, ACK, abort/reset and release. APUSYS uses its own RPMsg implementation; do not assign it to TinySys IPI merely because both exchange messages.
- **Still required:** Complete per-module source/parity and observable DT/ABI acceptance; proprietary algorithms excluded

**Purpose:** APUSYS/NPU normal-world kernel source/parity closure, not firmware reconstruction.

**Decision:** REGISTER PARTIAL. apusys and apu_top are normal-world source-actionable kernel code, not proprietary algorithms. Prior class-C blob-inventory ownership did not establish source parity; APU/MDLA RPMsg nodes were incorrectly attributed to camera consumers.

**Entry point:** [CLAUDE-HANDOFF.md](CLAUDE-HANDOFF.md). Canonical research: `reverse-engineering/accelerator-preparation/APUSYS-NPU-KERNEL/`. Workspace pack: `Reverse Engineer - PARTIAL/APUSYS-NPU-KERNEL/`.

**Exclusive primary kernel modules (2):** `apu_top.ko`, `apusys.ko`. Dependencies are references, not additional ownership.

[stock modules](stock-modules.tsv), [DT nodes](dt-nodes.tsv), [source candidates](source-candidates.tsv), [parity gaps](parity-gaps.tsv), [imports](imports.tsv), [exports](exports.tsv), [functions](functions.tsv), [data symbols](data-symbols.tsv), [donor ABI witnesses](abi-source-witnesses.tsv).

All APU/MDLA/MVPU RPMsg accelerator nodes previously attributed to CAMERA-HAL-ISP move to this kernel owner. Camera AIE/FD hardware stays CAMERA-ISP-KERNEL. GenieZone trusty-sapu remains the existing secure transport. Shared generic IOMMU/QoS/SSPM providers remain dependencies. APUware/NeuroPilot/neuron/NNAPI libraries and signed apusys firmware algorithms are retained binaries, not a claim of proven model execution.

No module rebuilt, hardware command executed or parity result created by this preparation. Published proof rows are preserved and labeled by axis; the component starts PARTIAL, never DONE.
