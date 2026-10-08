# Source-parity reconstruction sequence — MALI-GPU-KERNEL

1. Freeze MGM/protected allocator and GPU HAL exported interfaces; compare r44p1 baseline to r44p0 only as an alternative, not an assumed match.
2. Build MGM and protected allocator; recover resource/provider callbacks and data tables.
3. Close GPU HAL → gpufreq wrapper → mt6878 platform → GPU QoS → GED, resolving actual import cycles at ABI level with stock providers as initial operands.
4. Close Kbase object composition, CSF firmware-loading API, memory/VA/mmap/ioctl, scheduling, IRQ/fault/recovery and protected-mode paths.
5. Accept every owned module independently and then prove provider/consumer CRC/KCFI/DT compatibility across the assembled stack.

For **each** target in stock-modules.tsv, create its own function/data/ABI/residual ledger and isolated source patch series. Do not bulk-mark a scope DONE after compiling one binary. Preserve existing exact camera data/function proofs and closed provider source.

Apply [PARITY-STANDARD.md](../PARITY-STANDARD.md) completely, then verify imports/exports across the source-built provider graph and DT/observable ABI. Report new results in authoritative research commits before scoped workspace synchronization. Runtime tests are a separate, later authorized phase; none is permitted by this preparation assignment.
