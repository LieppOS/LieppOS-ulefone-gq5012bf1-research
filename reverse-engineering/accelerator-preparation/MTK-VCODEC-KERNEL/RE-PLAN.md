# Source-parity reconstruction sequence — MTK-VCODEC-KERNEL

> **Executed and closed.** Steps 1-5 below were completed by the reconstruction recorded in
> [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md): all five modules were accepted on
> every axis of [PARITY-STANDARD.md](../PARITY-STANDARD.md) plus the observable DT/ABI
> contract, from unmodified public source, with clean-checkout B1/B2 determinism. Runtime
> tests remain a separate, later authorized phase; none was performed.

1. Close dedicated vcodec clock module and common IRQ/DMA/power/provider helpers.
2. Reconstruct decoder and encoder object composition, FOURCC/control tables, buffer state machines and VCP message layouts independently.
3. Close VCU character-device/userspace bridge, compat translation and firmware-channel lifecycle.
4. Trace interrupt, fence/completion, failure/timeout/abort and reset recovery across both directions.
5. Accept five modules and source-visible Codec2/V4L2/DT interface equivalence; retain declared XML limits without claiming hardware success.

For **each** target in stock-modules.tsv, create its own function/data/ABI/residual ledger and isolated source patch series. Do not bulk-mark a scope DONE after compiling one binary. Preserve existing exact camera data/function proofs and closed provider source.

Apply [PARITY-STANDARD.md](../PARITY-STANDARD.md) completely, then verify imports/exports across the source-built provider graph and DT/observable ABI. Report new results in authoritative research commits before scoped workspace synchronization. Runtime tests are a separate, later authorized phase; none is permitted by this preparation assignment.
