# Hardware contract — MTK-MDP-KERNEL

MT6878 MDP/MML data-processing RDMA, resizer, WROT, color/HDR/AAL/TDSHP and mutex/config blocks in the 0x1f000000 region. MDP and MML are not the ISP, codec engines or DRM scanout driver. The exact DT node list provides real blocks rather than invented module names.

**Evidence:** [dt-nodes.tsv](dt-nodes.tsv) is decoded from `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb` (stock selected base+overlay). Each row retains all properties, exact parent-bus reg ranges, interrupt cells and resolved provider arguments. [dt-providers.tsv](dt-providers.tsv) resolves clock/power/IOMMU/mailbox/reset phandles where declared. Addresses are parent-bus addresses; verify `ranges` translations before calling them physical CPU addresses. Numeric IRQ cells are DT specs, not observed Linux IRQ numbers.

mdp_drv plus generic/platform MML interfaces; command construction/tile scheduling, buffer/fence lifecycle, DMA/IOMMU/SMI bandwidth, power/clock control and CMDQ execution. Distinguish generic command-queue engine from MDP clients, DRM attachment from full MDP reconstruction, and vendor PQ userspace from kernel block programming. Recover tile geometry, plane offsets/strides, job submit/complete/cancel/error handling and teardown.

**UNKNOWN:** missing register names, IRQ servicing semantics, electrical enablement, execution or throughput not evidenced by these static rows. `okay` and module loading never establish successful probe or execution. Runtime libraries only establish consumers/capability.
