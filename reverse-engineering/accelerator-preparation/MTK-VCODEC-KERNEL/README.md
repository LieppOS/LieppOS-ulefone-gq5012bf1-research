# MTK-VCODEC-KERNEL — PARTIAL preparation

**Purpose:** Hardware VCodec normal-world kernel source/parity closure, not firmware reconstruction.

**Decision:** REGISTER PARTIAL. Four codec/VCU normal-world drivers and their dedicated clock provider have donor targets but no complete module-level source/parity owner. Generic coverage was not a measured reconstruction.

**Entry point:** [CLAUDE-HANDOFF.md](CLAUDE-HANDOFF.md). Canonical research: `reverse-engineering/accelerator-preparation/MTK-VCODEC-KERNEL/`. Workspace pack: `Reverse Engineer - PARTIAL/MTK-VCODEC-KERNEL/`.

**Exclusive primary kernel modules (5):** `mtk-vcodec-common.ko`, `mtk-vcodec-dec-v1.ko`, `mtk-vcodec-enc-v1.ko`, `mtk-vcu.ko`, `clk-mt6878-vcodec.ko`. Dependencies are references, not additional ownership.

[stock modules](stock-modules.tsv), [DT nodes](dt-nodes.tsv), [source candidates](source-candidates.tsv), [parity gaps](parity-gaps.tsv), [imports](imports.tsv), [exports](exports.tsv), [functions](functions.tsv), [data symbols](data-symbols.tsv), [donor ABI witnesses](abi-source-witnesses.tsv).

VCP host/status modules belong to the auxiliary component; VCP firmware algorithms and Codec2/vendor codec implementations are proprietary. Shared CMDQ/IOMMU/SMI/power providers are not duplicated. Existing generic source triage was not module-level source/parity closure.

No module rebuilt, hardware command executed or parity result created by this preparation. Published proof rows are preserved and labeled by axis; the component starts PARTIAL, never DONE.
