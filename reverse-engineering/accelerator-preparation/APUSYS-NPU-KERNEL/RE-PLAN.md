# Source-parity reconstruction sequence — APUSYS-NPU-KERNEL

1. Close apu_top power initialization, OPP/DVFS/thermal callbacks, unwind and suspend/reset state machine.
2. Split the existing apusys Kbuild object list into middleware, remoteproc/RPMsg, APUMMU/reviser, EDMA, MDLA and MVPU work units; do not invent standalone mdla.ko or mvpu.ko.
3. Reconstruct shared-memory and command-submit/complete/error ABI, including compat ioctls and secure-boundary calls.
4. Close interrupt, mailbox, RPMsg readiness, timeout, recovery/reset and teardown paths against stock.
5. Accept both modules and verify every exposed provider/callback against stock consumers.

For **each** target in stock-modules.tsv, create its own function/data/ABI/residual ledger and isolated source patch series. Do not bulk-mark a scope DONE after compiling one binary. Preserve existing exact camera data/function proofs and closed provider source.

Apply [PARITY-STANDARD.md](../PARITY-STANDARD.md) completely, then verify imports/exports across the source-built provider graph and DT/observable ABI. Report new results in authoritative research commits before scoped workspace synchronization. Runtime tests are a separate, later authorized phase; none is permitted by this preparation assignment.
