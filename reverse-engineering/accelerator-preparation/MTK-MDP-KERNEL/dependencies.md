# Dependencies and singleton ownership — MTK-MDP-KERNEL

**Prerequisites:** GKI-KMI-BASELINE; existing DRM; generic CMDQ/SMI/IOMMU; VCP host/status.

**Owned modules:** `mdp_drv_mt6878.ko`, `mtk-mml.ko`, `mtk-mml-mt6878.ko`, `clk-mt6878-mdpsys.ko`.

MEDIATEK-DRM remains DONE for its explicitly proved DRM/panel modules; that result does not close mdp_drv or either MML binary. Generic mtk-cmdq-drv-ext/cmdq-platform/helpers remain platform dependencies; cmdq-sec-drv remains the existing GZ-TZ-SYSTEM scope. Do not absorb video codec or camera ISP owners. Preserve userspace PQ algorithms as proprietary.

[Master dependency edges](../dependency-edges.tsv) resolve stock imports by symbol and CRC; each row carries consumer/provider/owner. The load order and legacy modinfo dependencies are recorded separately in stock-modules.tsv. `modules.dep` can be transitive and legacy modinfo can name obsolete provider identities; neither overrides the actual export/CRC graph.

Raw direct modinfo dependency sets: `cmdq_helper_inf,mtk-cmdq-drv-ext,iommu_debug,mtk-icc-core,system_heap,mmprofile,aee_aed,mtk-smi-dbg,mtk-mmdvfs-v3; mtk-cmdq-drv-ext,mtk-mmdvfs-v3,mtk-icc-core,mtk_slbc,mtk-smi-dbg,aee_aed,mtk_sync,system_heap,tinysys-scmi; mtk-mml,mtk-cmdq-drv-ext; clk-common`. These names are not a list of new targets. UNKNOWN provider/type provenance must be resolved against existing stock export/KMI ledgers, not fabricated. Preserve generic platform providers and explicitly closed modules.

For cycles, freeze mutually shared headers/provider ABI, use unchanged stock provider operands during initial isolation, then verify the assembled reconstructed graph; copied stock symvers is an oracle, not source/type proof.
