# Hardware contract — CAMERA-ISP-KERNEL

ISP7sp FE/RAW/YUV/RMS/MRAW/CAMSV and P2 DIP/TRAW/WPE/ME/PQDIP, SENINF/CSI, CCD/CCU, AIE/FD, DPE, PDA and VMM interfaces. Existing camera-stack/notes/isp-stack.md specifies four CSI ports, nvmem PHY tuning and camera power domains. Sensor dies, EEPROMs, lens/VCM/OIS and camera rails retain their named DONE owners.

**Evidence:** [dt-nodes.tsv](dt-nodes.tsv) is decoded from `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb` (stock selected base+overlay). Each row retains all properties, exact parent-bus reg ranges, interrupt cells and resolved provider arguments. [dt-providers.tsv](dt-providers.tsv) resolves clock/power/IOMMU/mailbox/reset phandles where declared. Addresses are parent-bus addresses; verify `ranges` translations before calling them physical CPU addresses. Numeric IRQ cells are DT specs, not observed Linux IRQ numbers.

Camsys/media/V4L2 scheduling, request/buffer DMA lifecycle and camera IOMMU integration; IMG_SYS/HCP command/tuning buffers and CMDQ; CCD/CCU normal-world communication; DPE/PDA/AIE vendor ioctls; VMM voltage/notifier ABI; imgsensor framework/glue and C2PS scheduling hooks. Sensor TUs are named subscopes inside imgsensor.ko, not duplicate whole-module ownership. Stock .modinfo includes legacy CCU dependency names; actual CRC-resolved exports point to mtk_ccuv.ko—do not invent mtk_ccu.ko or mtk_ccu_mssv.ko absent from the 457-module universe.

**UNKNOWN:** missing register names, IRQ servicing semantics, electrical enablement, execution or throughput not evidenced by these static rows. `okay` and module loading never establish successful probe or execution. Runtime libraries only establish consumers/capability.
