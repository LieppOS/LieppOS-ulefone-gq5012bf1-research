# MTK-MDP-KERNEL — PARTIAL preparation

Status: PARTIAL

- **Subsystem:** Accelerators / MDP
- **Hardware identity:** MT6878 MDP/MML data-processing RDMA, resizer, WROT, color/HDR/AAL/TDSHP and mutex/config blocks in the 0x1f000000 region. MDP and MML are not the ISP, codec engines or DRM scanout driver. The exact DT node list provides real blocks rather than invented module names.
- **Stock artifact:** `mdp_drv_mt6878.ko`, `mtk-mml.ko`, `mtk-mml-mt6878.ko`, `clk-mt6878-mdpsys.ko`
- **Interfaces:** mdp_drv plus generic/platform MML interfaces; command construction/tile scheduling, buffer/fence lifecycle, DMA/IOMMU/SMI bandwidth, power/clock control and CMDQ execution. Distinguish generic command-queue engine from MDP clients, DRM attachment from full MDP reconstruction, and vendor PQ userspace from kernel block programming. Recover tile geometry, plane offsets/strides, job submit/complete/cancel/error handling and teardown.
- **Still required:** Complete per-module source/parity and observable DT/ABI acceptance; proprietary algorithms excluded

**Purpose:** MDP normal-world kernel source/parity closure, not firmware reconstruction.

**Decision:** REGISTER PARTIAL. mdp_drv and the two MML modules are distinct from mediatek-drm. The DRM DONE scope explicitly closes DRM/panel modules, not MDP/MML; no MDP byte/semantic parity evidence was found. Keep generic CMDQ and reconstructed secure CMDQ outside this component.

**Entry point:** [CLAUDE-HANDOFF.md](CLAUDE-HANDOFF.md). Canonical research: `reverse-engineering/accelerator-preparation/MTK-MDP-KERNEL/`. Workspace pack: `Reverse Engineer - PARTIAL/MTK-MDP-KERNEL/`.

**Exclusive primary kernel modules (4):** `mdp_drv_mt6878.ko`, `mtk-mml.ko`, `mtk-mml-mt6878.ko`, `clk-mt6878-mdpsys.ko`. Dependencies are references, not additional ownership.

[stock modules](stock-modules.tsv), [DT nodes](dt-nodes.tsv), [source candidates](source-candidates.tsv), [parity gaps](parity-gaps.tsv), [imports](imports.tsv), [exports](exports.tsv), [functions](functions.tsv), [data symbols](data-symbols.tsv), [donor ABI witnesses](abi-source-witnesses.tsv).

MEDIATEK-DRM remains DONE for its explicitly proved DRM/panel modules; that result does not close mdp_drv or either MML binary. Generic mtk-cmdq-drv-ext/cmdq-platform/helpers remain platform dependencies; cmdq-sec-drv remains the existing GZ-TZ-SYSTEM scope. Do not absorb video codec or camera ISP owners. Preserve userspace PQ algorithms as proprietary.

No module rebuilt, hardware command executed or parity result created by this preparation. Published proof rows are preserved and labeled by axis; the component starts PARTIAL, never DONE.
