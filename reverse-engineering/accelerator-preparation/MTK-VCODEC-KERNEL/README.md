# MTK-VCODEC-KERNEL — PARTIAL preparation

Status: PARTIAL

- **Subsystem:** Accelerators / Hardware VCodec
- **Hardware identity:** MT6878 decoder vdec@16000000, encoder venc@17000000, dedicated vcodec clocks and VCP codec IOMMU domains. Exact registers, interrupts and power/clock/domain references are in dt-nodes.tsv. JPEG and display/MDP blocks are distinct, not silently added to this scope.
- **Stock artifact:** `mtk-vcodec-common.ko`, `mtk-vcodec-dec-v1.ko`, `mtk-vcodec-enc-v1.ko`, `mtk-vcu.ko`, `clk-mt6878-vcodec.ko`
- **Interfaces:** MediaTek V4L2 decoder/encoder and common driver; VCU bridge and VCP firmware ABI, native/compat ioctls, video device registration, input/output buffer ownership, DMA/IOMMU, interrupt completion, stream-on/off/abort and timeout recovery. Stock codec XML declarations and donor FOURCC evidence are recorded separately: neither proves codec execution or that the unchanged generic donor reproduces shipped binaries. Codec2/userspace consumer candidates are listed without asserting a complete call graph.
- **Still required:** Complete per-module source/parity and observable DT/ABI acceptance; proprietary algorithms excluded

**Purpose:** Hardware VCodec normal-world kernel source/parity closure, not firmware reconstruction.

**Decision:** REGISTER PARTIAL. Four codec/VCU normal-world drivers and their dedicated clock provider have donor targets but no complete module-level source/parity owner. Generic coverage was not a measured reconstruction.

**Entry point:** [CLAUDE-HANDOFF.md](CLAUDE-HANDOFF.md). Canonical research: `reverse-engineering/accelerator-preparation/MTK-VCODEC-KERNEL/`. Workspace pack: `Reverse Engineer - PARTIAL/MTK-VCODEC-KERNEL/`.

**Exclusive primary kernel modules (5):** `mtk-vcodec-common.ko`, `mtk-vcodec-dec-v1.ko`, `mtk-vcodec-enc-v1.ko`, `mtk-vcu.ko`, `clk-mt6878-vcodec.ko`. Dependencies are references, not additional ownership.

[stock modules](stock-modules.tsv), [DT nodes](dt-nodes.tsv), [source candidates](source-candidates.tsv), [parity gaps](parity-gaps.tsv), [imports](imports.tsv), [exports](exports.tsv), [functions](functions.tsv), [data symbols](data-symbols.tsv), [donor ABI witnesses](abi-source-witnesses.tsv).

VCP host/status modules belong to the auxiliary component; VCP firmware algorithms and Codec2/vendor codec implementations are proprietary. Shared CMDQ/IOMMU/SMI/power providers are not duplicated. Existing generic source triage was not module-level source/parity closure.

No module rebuilt, hardware command executed or parity result created by this preparation. Published proof rows are preserved and labeled by axis; the component starts PARTIAL, never DONE.
