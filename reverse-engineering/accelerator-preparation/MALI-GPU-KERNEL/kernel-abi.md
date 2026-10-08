# Kernel/userspace ABI — MALI-GPU-KERNEL

Kbase memory/context/queue management and mmap/ioctl paths; MGM memory groups and protected allocator; GED, GPU HAL callbacks, GPU QoS and gpufreq wrapper/platform interfaces. Trace kbase context creation → GPU VA allocation/import/map → CSF scheduling → completion/fault cleanup; then protected allocation and normal-world secure-heap calls. `/dev/mali0` is the expected Kbase ABI, not a newly observed binding. Numeric commands and layouts must be checked against stock handlers; source definitions alone are not parity.

**Static witnesses:** [functions.tsv](functions.tsv) identifies each exact symbol/section/offset/size; [imports.tsv](imports.tsv) pins modversion CRCs and known stock providers; [exports.tsv](exports.tsv) pins export buckets/CRCs; [abi-source-witnesses.tsv](abi-source-witnesses.tsv) gives precise source file/line/hash for IOCTLs, fops, buffers, IRQ, power, recovery, firmware and transport candidates. Source lines are explicitly DONOR—not accepted stock behavior.

**Remaining contract work:** enumerate each device node, ioctl direction/number/struct size and compat layout, mmap offset/cache behavior, poll/fence semantics, queue states, buffer ownership, error returns and teardown. Recover stock call sites and data/relocations before asserting numerical equivalence. Read the [userspace consumer list](userspace-consumers.tsv); it is not proof of every edge or live use.

Kernel release is the exact stock GKI/KMI baseline, not the host kernel. Do not replace natural CRC/KCFI generation with forced constants or CRC stamping as a proof of reconstructed types.
