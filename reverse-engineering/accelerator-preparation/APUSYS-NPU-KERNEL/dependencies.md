# Dependencies and singleton ownership — APUSYS-NPU-KERNEL

**Prerequisites:** GKI-KMI-BASELINE; shared IOMMU/QoS/power providers; signed apusys.img retained.

**Owned modules:** `apu_top.ko`, `apusys.ko`.

All APU/MDLA/MVPU RPMsg accelerator nodes previously attributed to CAMERA-HAL-ISP move to this kernel owner. Camera AIE/FD hardware stays CAMERA-ISP-KERNEL. GenieZone trusty-sapu remains the existing secure transport. Shared generic IOMMU/QoS/SSPM providers remain dependencies. APUware/NeuroPilot/neuron/NNAPI libraries and signed apusys firmware algorithms are retained binaries, not a claim of proven model execution.

[Master dependency edges](../dependency-edges.tsv) resolve stock imports by symbol and CRC; each row carries consumer/provider/owner. The load order and legacy modinfo dependencies are recorded separately in stock-modules.tsv. `modules.dep` can be transitive and legacy modinfo can name obsolete provider identities; neither overrides the actual export/CRC graph.

Raw direct modinfo dependency sets: `aee_aed; apu_top,aee_aed,mtk_slbc,mtk_qos,mtk_peak_power_budget,mrdump,iommu_debug`. These names are not a list of new targets. UNKNOWN provider/type provenance must be resolved against existing stock export/KMI ledgers, not fabricated. Preserve generic platform providers and explicitly closed modules.

For cycles, freeze mutually shared headers/provider ABI, use unchanged stock provider operands during initial isolation, then verify the assembled reconstructed graph; copied stock symvers is an oracle, not source/type proof.
