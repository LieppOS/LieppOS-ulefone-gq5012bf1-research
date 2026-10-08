# MTK-VCODEC-KERNEL — DONE

Status: DONE — all five owned modules rebuild from unmodified public ALPS source
(`5e415e059253`) and match stock byte-for-byte except their 20-byte GNU build IDs.
Start at [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md) and [SOURCE.md](SOURCE.md).

- **Subsystem:** Accelerators / Hardware VCodec
- **Hardware identity:** MT6878 decoder vdec@16000000, encoder venc@17000000, dedicated vcodec clocks and VCP codec IOMMU domains. Exact registers, interrupts and power/clock/domain references are in dt-nodes.tsv. JPEG and display/MDP blocks are distinct, not silently added to this scope.
- **Stock artifact:** `mtk-vcodec-common.ko`, `mtk-vcodec-dec-v1.ko`, `mtk-vcodec-enc-v1.ko`, `mtk-vcu.ko`, `clk-mt6878-vcodec.ko`
- **Interfaces:** MediaTek V4L2 decoder/encoder and common driver; VCU bridge and VCP firmware ABI, native/compat ioctls, video device registration, input/output buffer ownership, DMA/IOMMU, interrupt completion, stream-on/off/abort and timeout recovery. Stock codec XML declarations and donor FOURCC evidence are recorded separately: neither proves codec execution or that the unchanged generic donor reproduces shipped binaries. Codec2/userspace consumer candidates are listed without asserting a complete call graph.
- **Still required:** nothing static. Runtime-only: probe, VCP firmware handshake, real decode/encode, interrupt/recovery and DVFS/thermal behaviour (see [source-to-userspace-contract.md](source-to-userspace-contract.md) \u00a73)

**Purpose:** Hardware VCodec normal-world kernel source/parity closure, not firmware reconstruction.

**Decision:** DONE. The four codec/VCU normal-world drivers and the dedicated clock provider are reconstructed from exact public source with full static parity and clean-checkout B1/B2 determinism; see [parity-gaps.tsv](parity-gaps.tsv) and [stale-claims.md](stale-claims.md).

**Entry point:** [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md) (the original [CLAUDE-HANDOFF.md](CLAUDE-HANDOFF.md) is preserved as the preparation record). Canonical research: `reverse-engineering/accelerator-preparation/MTK-VCODEC-KERNEL/`. Workspace pack: `Reverse Engineer - DONE/MTK-VCODEC-KERNEL/`.

**Exclusive primary kernel modules (5):** `mtk-vcodec-common.ko`, `mtk-vcodec-dec-v1.ko`, `mtk-vcodec-enc-v1.ko`, `mtk-vcu.ko`, `clk-mt6878-vcodec.ko`. Dependencies are references, not additional ownership.

[stock modules](stock-modules.tsv), [DT nodes](dt-nodes.tsv), [source candidates](source-candidates.tsv), [parity gaps](parity-gaps.tsv), [imports](imports.tsv), [exports](exports.tsv), [functions](functions.tsv), [data symbols](data-symbols.tsv), [donor ABI witnesses](abi-source-witnesses.tsv).

VCP host/status modules belong to the auxiliary component; VCP firmware algorithms and Codec2/vendor codec implementations are proprietary. Shared CMDQ/IOMMU/SMI/power providers are not duplicated. Existing generic source triage was not module-level source/parity closure.

The original preparation created no rebuild or parity result; every parity statement in this pack now comes from the measured reconstruction recorded in `evidence/reconstruction/`. No hardware command was executed at any stage.
