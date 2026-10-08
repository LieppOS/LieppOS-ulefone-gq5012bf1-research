# Dependencies and singleton ownership — MTK-VCODEC-KERNEL

**Prerequisites:** GKI-KMI-BASELINE; VCP host/status; shared DMA/IOMMU/CMDQ/power.

**Owned modules:** `mtk-vcodec-common.ko`, `mtk-vcodec-dec-v1.ko`, `mtk-vcodec-enc-v1.ko`, `mtk-vcu.ko`, `clk-mt6878-vcodec.ko`.

VCP host/status modules belong to the auxiliary component; VCP firmware algorithms and Codec2/vendor codec implementations are proprietary. Shared CMDQ/IOMMU/SMI/power providers are not duplicated. Existing generic source triage was not module-level source/parity closure.

[Master dependency edges](../dependency-edges.tsv) resolve stock imports by symbol and CRC; each row carries consumer/provider/owner. The load order and legacy modinfo dependencies are recorded separately in stock-modules.tsv. `modules.dep` can be transitive and legacy modinfo can name obsolete provider identities; neither overrides the actual export/CRC graph.

Raw direct modinfo dependency sets: `scheduler,system_heap; mtk-vcodec-common,mtk-icc-core,vcp,mtk_tinysys_ipi,emi,mtk-mmdvfs-v3,vcp_status,system_heap,iommu_debug,mtk_slbc; mtk-vcodec-common,mtk-icc-core,mtk-mmdvfs-v3,mtk-smi-dbg,vcp,mtk_slbc,mtk_tinysys_ipi,emi,mtk-smi,iommu_debug; mtk-vcodec-common,mtk-cmdq-drv-ext,vcp; clk-common`. These names are not a list of new targets. UNKNOWN provider/type provenance must be resolved against existing stock export/KMI ledgers, not fabricated. Preserve generic platform providers and explicitly closed modules.

For cycles, freeze mutually shared headers/provider ABI, use unchanged stock provider operands during initial isolation, then verify the assembled reconstructed graph; copied stock symvers is an oracle, not source/type proof.
