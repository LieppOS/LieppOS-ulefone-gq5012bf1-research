# Kernel/userspace ABI — MTK-VCODEC-KERNEL

MediaTek V4L2 decoder/encoder and common driver; VCU bridge and VCP firmware ABI, native/compat ioctls, video device registration, input/output buffer ownership, DMA/IOMMU, interrupt completion, stream-on/off/abort and timeout recovery. Stock codec XML declarations and donor FOURCC evidence are recorded separately: neither proves codec execution or that the unchanged generic donor reproduces shipped binaries. Codec2/userspace consumer candidates are listed without asserting a complete call graph.

**Static witnesses:** [functions.tsv](functions.tsv) identifies each exact symbol/section/offset/size; [imports.tsv](imports.tsv) pins modversion CRCs and known stock providers; [exports.tsv](exports.tsv) pins export buckets/CRCs; [abi-source-witnesses.tsv](abi-source-witnesses.tsv) gives precise source file/line/hash for IOCTLs, fops, buffers, IRQ, power, recovery, firmware and transport candidates. Source lines are explicitly DONOR—not accepted stock behavior.

**Remaining contract work:** enumerate each device node, ioctl direction/number/struct size and compat layout, mmap offset/cache behavior, poll/fence semantics, queue states, buffer ownership, error returns and teardown. Recover stock call sites and data/relocations before asserting numerical equivalence. Read the [userspace consumer list](userspace-consumers.tsv); it is not proof of every edge or live use.

Kernel release is the exact stock GKI/KMI baseline, not the host kernel. Do not replace natural CRC/KCFI generation with forced constants or CRC stamping as a proof of reconstructed types.
