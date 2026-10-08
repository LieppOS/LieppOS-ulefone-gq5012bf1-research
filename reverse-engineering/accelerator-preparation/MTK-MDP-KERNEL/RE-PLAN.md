# Source-parity reconstruction sequence — MTK-MDP-KERNEL

> **Executed and closed.** The steps below were completed by the reconstruction recorded in
> [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md): all four modules were accepted on
> every axis of [PARITY-STANDARD.md](../PARITY-STANDARD.md) plus the observable DT/ABI
> contract, from unmodified public source, with clean-checkout B1/B2 determinism. Runtime
> tests remain a separate, later authorized phase; none was performed.

1. Close clk-mt6878-mdpsys and mdp_drv object/target composition against stock.
2. Close mtk-mml common interfaces, job/tile/config lifetime and shared-resource arbitration.
3. Close mtk-mml-mt6878 block tables, per-engine clock/IRQ programming, platform quirks and command generation.
4. Verify CMDQ, SMI/IOMMU, DRM and optional VCP boundary contracts without reconstructing their already owned modules.
5. Accept four module parity packets and complete the observable submit/buffer/fence/error ABI.

For **each** target in stock-modules.tsv, create its own function/data/ABI/residual ledger and isolated source patch series. Do not bulk-mark a scope DONE after compiling one binary. Preserve existing exact camera data/function proofs and closed provider source.

Apply [PARITY-STANDARD.md](../PARITY-STANDARD.md) completely, then verify imports/exports across the source-built provider graph and DT/observable ABI. Report new results in authoritative research commits before scoped workspace synchronization. Runtime tests are a separate, later authorized phase; none is permitted by this preparation assignment.
