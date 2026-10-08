# Hardware contract — MTK-VCODEC-KERNEL

MT6878 decoder vdec@16000000, encoder venc@17000000, dedicated vcodec clocks and VCP codec IOMMU domains. Exact registers, interrupts and power/clock/domain references are in dt-nodes.tsv. JPEG and display/MDP blocks are distinct, not silently added to this scope.

**Evidence:** [dt-nodes.tsv](dt-nodes.tsv) is decoded from `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb` (stock selected base+overlay). Each row retains all properties, exact parent-bus reg ranges, interrupt cells and resolved provider arguments. [dt-providers.tsv](dt-providers.tsv) resolves clock/power/IOMMU/mailbox/reset phandles where declared. Addresses are parent-bus addresses; verify `ranges` translations before calling them physical CPU addresses. Numeric IRQ cells are DT specs, not observed Linux IRQ numbers.

MediaTek V4L2 decoder/encoder and common driver; VCU bridge and VCP firmware ABI, native/compat ioctls, video device registration, input/output buffer ownership, DMA/IOMMU, interrupt completion, stream-on/off/abort and timeout recovery. Stock codec XML declarations and donor FOURCC evidence are recorded separately: neither proves codec execution or that the unchanged generic donor reproduces shipped binaries. Codec2/userspace consumer candidates are listed without asserting a complete call graph.

**UNKNOWN:** missing register names, IRQ servicing semantics, electrical enablement, execution or throughput not evidenced by these static rows. `okay` and module loading never establish successful probe or execution. Runtime libraries only establish consumers/capability.
