# Source-parity reconstruction sequence — GPU-AI-AUX-KERNEL-INTERFACES

1. Reuse DONE mailbox/RPMsg/IPI source and exact provider CRC/KCFI evidence; freeze all client-facing headers.
2. Close gpueb probe/shared-memory/IRQ/channel table/power/readiness/reset/recovery and exported callback interfaces.
3. Close vcp_status early provider and vcp host boot/reserved-memory/mailbox/feature/suspend/recovery code in dependency order.
4. Check GPU, codec, camera and MDP client imports/callbacks against the reconstructed providers.
5. Accept three independent full-module packets; do not change SCP/ADSP DONE status or promise firmware parity.

For **each** target in stock-modules.tsv, create its own function/data/ABI/residual ledger and isolated source patch series. Do not bulk-mark a scope DONE after compiling one binary. Preserve existing exact camera data/function proofs and closed provider source.

Apply [PARITY-STANDARD.md](../PARITY-STANDARD.md) completely, then verify imports/exports across the source-built provider graph and DT/observable ABI. Report new results in authoritative research commits before scoped workspace synchronization. Runtime tests are a separate, later authorized phase; none is permitted by this preparation assignment.
