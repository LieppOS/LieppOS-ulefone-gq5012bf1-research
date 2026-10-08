# Kernel/userspace ABI — CAMERA-ISP-KERNEL

Camsys/media/V4L2 scheduling, request/buffer DMA lifecycle and camera IOMMU integration; IMG_SYS/HCP command/tuning buffers and CMDQ; CCD/CCU normal-world communication; DPE/PDA/AIE vendor ioctls; VMM voltage/notifier ABI; imgsensor framework/glue and C2PS scheduling hooks. Sensor TUs are named subscopes inside imgsensor.ko, not duplicate whole-module ownership. Stock .modinfo includes legacy CCU dependency names; actual CRC-resolved exports point to mtk_ccuv.ko—do not invent mtk_ccu.ko or mtk_ccu_mssv.ko absent from the 457-module universe.

**Static witnesses:** [functions.tsv](functions.tsv) identifies each exact symbol/section/offset/size; [imports.tsv](imports.tsv) pins modversion CRCs and known stock providers; [exports.tsv](exports.tsv) pins export buckets/CRCs; [abi-source-witnesses.tsv](abi-source-witnesses.tsv) gives precise source file/line/hash for IOCTLs, fops, buffers, IRQ, power, recovery, firmware and transport candidates. Source lines are explicitly DONOR—not accepted stock behavior.

**Remaining contract work:** enumerate each device node, ioctl direction/number/struct size and compat layout, mmap offset/cache behavior, poll/fence semantics, queue states, buffer ownership, error returns and teardown. Recover stock call sites and data/relocations before asserting numerical equivalence. Read the [userspace consumer list](userspace-consumers.tsv); it is not proof of every edge or live use.

Kernel release is the exact stock GKI/KMI baseline, not the host kernel. Do not replace natural CRC/KCFI generation with forced constants or CRC stamping as a proof of reconstructed types.
