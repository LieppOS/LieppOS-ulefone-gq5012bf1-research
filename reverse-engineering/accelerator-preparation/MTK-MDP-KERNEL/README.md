# MTK-MDP-KERNEL — DONE

Status: DONE — all four owned modules rebuild from unmodified public ALPS source
(`5e415e059253`) and match stock byte-for-byte except their 20-byte GNU build IDs.
Start at [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md) and [SOURCE.md](SOURCE.md).

- **Subsystem:** Accelerators / MDP
- **Hardware identity:** MT6878 MDP/MML data-processing RDMA, resizer, WROT, color/HDR/AAL/TDSHP and mutex/config blocks in the 0x1f000000 region. MDP and MML are not the ISP, codec engines or DRM scanout driver. The exact DT node list provides real blocks rather than invented module names.
- **Stock artifact:** `mdp_drv_mt6878.ko`, `mtk-mml.ko`, `mtk-mml-mt6878.ko`, `clk-mt6878-mdpsys.ko`
- **Interfaces:** mdp_drv plus generic/platform MML interfaces; command construction/tile scheduling, buffer/fence lifecycle, DMA/IOMMU/SMI bandwidth, power/clock control and CMDQ execution. Distinguish generic command-queue engine from MDP clients, DRM attachment from full MDP reconstruction, and vendor PQ userspace from kernel block programming. Recover tile geometry, plane offsets/strides, job submit/complete/cancel/error handling and teardown.
- **Still required:** nothing static. Runtime-only: probe, CMDQ submission, DMA/IOMMU, interrupt, timeout/recovery and clock/power behaviour (see [source-to-userspace-contract.md](source-to-userspace-contract.md) §4). Vendor PQ algorithms remain proprietary and excluded.

**Purpose:** MDP normal-world kernel source/parity closure, not firmware reconstruction.

**Decision:** DONE. mdp_drv and the two MML modules are distinct from mediatek-drm and are now reconstructed from exact public source with full static parity and clean-checkout B1/B2 determinism; see [parity-gaps.tsv](parity-gaps.tsv) and [stale-claims.md](stale-claims.md). Generic CMDQ and secure CMDQ remain outside this component.

**Entry point:** [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md) (the original [CLAUDE-HANDOFF.md](CLAUDE-HANDOFF.md) is preserved as the preparation record). Canonical research: `reverse-engineering/accelerator-preparation/MTK-MDP-KERNEL/`. Workspace pack: `Reverse Engineer - DONE/MTK-MDP-KERNEL/`.

**Exclusive primary kernel modules (4):** `mdp_drv_mt6878.ko`, `mtk-mml.ko`, `mtk-mml-mt6878.ko`, `clk-mt6878-mdpsys.ko`. Dependencies are references, not additional ownership.

[stock modules](stock-modules.tsv), [DT nodes](dt-nodes.tsv), [measured DT topology](dt-topology.tsv), [source candidates](source-candidates.tsv), [parity gaps](parity-gaps.tsv), [function parity](function-parity.tsv), [data parity](data-parity.tsv), [imports](imports.tsv), [exports](exports.tsv), [functions](functions.tsv), [data symbols](data-symbols.tsv), [donor ABI witnesses](abi-source-witnesses.tsv).

MEDIATEK-DRM remains DONE for its explicitly proved DRM/panel modules; that result does not close mdp_drv or either MML binary. Generic mtk-cmdq-drv-ext/cmdq-platform/helpers remain platform dependencies; cmdq-sec-drv remains the existing GZ-TZ-SYSTEM scope. Do not absorb video codec or camera ISP owners. Preserve userspace PQ algorithms as proprietary.

The original preparation created no rebuild or parity result; every parity statement in this pack now comes from the measured reconstruction recorded in `evidence/reconstruction/`. No hardware command was executed at any stage.
