# Hardware contract — APUSYS-NPU-KERNEL

MT6878 APU RV complex at apusys-rv@190e1000, apu-top-3@1c000000, APUMMU, APU IOMMU banks and MDLA/MVPU/EDMA/RPMsg channel declarations. The monolithic apusys.ko contains multiple IP generations: alias presence does not mean every generation is enabled. Separate board DT instances from dormant code.

**Evidence:** [dt-nodes.tsv](dt-nodes.tsv) is decoded from `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb` (stock selected base+overlay). Each row retains all properties, exact parent-bus reg ranges, interrupt cells and resolved provider arguments. [dt-providers.tsv](dt-providers.tsv) resolves clock/power/IOMMU/mailbox/reset phandles where declared. Addresses are parent-bus addresses; verify `ranges` translations before calling them physical CPU addresses. Numeric IRQ cells are DT specs, not observed Linux IRQ numbers.

apu_top power/DVFS callbacks; apusys middleware command submission, buffer/shared-memory management, APUMMU/reviser translation, RPMsg/mailbox/interrupt transport, EDMA/MDLA/MVPU completion and recovery. Extract APUSYS ioctl command numbers and native/compat layouts from source witnesses and compare stock switch paths. Recover ownership of each buffer through allocation, map, submit, ACK, abort/reset and release. APUSYS uses its own RPMsg implementation; do not assign it to TinySys IPI merely because both exchange messages.

**UNKNOWN:** missing register names, IRQ servicing semantics, electrical enablement, execution or throughput not evidenced by these static rows. `okay` and module loading never establish successful probe or execution. Runtime libraries only establish consumers/capability.
