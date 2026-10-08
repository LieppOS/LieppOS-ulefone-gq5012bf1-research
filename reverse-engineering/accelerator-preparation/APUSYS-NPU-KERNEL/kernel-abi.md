# Kernel/userspace ABI — APUSYS-NPU-KERNEL

apu_top power/DVFS callbacks; apusys middleware command submission, buffer/shared-memory management, APUMMU/reviser translation, RPMsg/mailbox/interrupt transport, EDMA/MDLA/MVPU completion and recovery. Extract APUSYS ioctl command numbers and native/compat layouts from source witnesses and compare stock switch paths. Recover ownership of each buffer through allocation, map, submit, ACK, abort/reset and release. APUSYS uses its own RPMsg implementation; do not assign it to TinySys IPI merely because both exchange messages.

**Static witnesses:** [functions.tsv](functions.tsv) identifies each exact symbol/section/offset/size; [imports.tsv](imports.tsv) pins modversion CRCs and known stock providers; [exports.tsv](exports.tsv) pins export buckets/CRCs; [abi-source-witnesses.tsv](abi-source-witnesses.tsv) gives precise source file/line/hash for IOCTLs, fops, buffers, IRQ, power, recovery, firmware and transport candidates. Source lines are explicitly DONOR—not accepted stock behavior.

**Remaining contract work:** enumerate each device node, ioctl direction/number/struct size and compat layout, mmap offset/cache behavior, poll/fence semantics, queue states, buffer ownership, error returns and teardown. Recover stock call sites and data/relocations before asserting numerical equivalence. Read the [userspace consumer list](userspace-consumers.tsv); it is not proof of every edge or live use.

Kernel release is the exact stock GKI/KMI baseline, not the host kernel. Do not replace natural CRC/KCFI generation with forced constants or CRC stamping as a proof of reconstructed types.
