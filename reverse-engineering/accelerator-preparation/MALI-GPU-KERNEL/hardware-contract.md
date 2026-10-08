# Hardware contract — MALI-GPU-KERNEL

Valhall/CSF KMD on MT6878; merged DT has mali@13000000 and g3d-brisket@13fb0000. Exact GPU_ID/revision/core count is UNKNOWN from this static pass; do not substitute a marketing GPU designation. Register ranges, raw GIC interrupt cells, clocks, power domains and provider arguments are recorded per node.

**Evidence:** [dt-nodes.tsv](dt-nodes.tsv) is decoded from `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb` (stock selected base+overlay). Each row retains all properties, exact parent-bus reg ranges, interrupt cells and resolved provider arguments. [dt-providers.tsv](dt-providers.tsv) resolves clock/power/IOMMU/mailbox/reset phandles where declared. Addresses are parent-bus addresses; verify `ranges` translations before calling them physical CPU addresses. Numeric IRQ cells are DT specs, not observed Linux IRQ numbers.

Kbase memory/context/queue management and mmap/ioctl paths; MGM memory groups and protected allocator; GED, GPU HAL callbacks, GPU QoS and gpufreq wrapper/platform interfaces. Trace kbase context creation → GPU VA allocation/import/map → CSF scheduling → completion/fault cleanup; then protected allocation and normal-world secure-heap calls. `/dev/mali0` is the expected Kbase ABI, not a newly observed binding. Numeric commands and layouts must be checked against stock handlers; source definitions alone are not parity.

**UNKNOWN:** missing register names, IRQ servicing semantics, electrical enablement, execution or throughput not evidenced by these static rows. `okay` and module loading never establish successful probe or execution. Runtime libraries only establish consumers/capability.
