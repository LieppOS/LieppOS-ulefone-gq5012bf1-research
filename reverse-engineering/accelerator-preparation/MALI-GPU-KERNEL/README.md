# MALI-GPU-KERNEL — PARTIAL preparation

Status: PARTIAL

- **Subsystem:** Accelerators / Mali GPU
- **Hardware identity:** Valhall/CSF KMD on MT6878; merged DT has mali@13000000 and g3d-brisket@13fb0000. Exact GPU_ID/revision/core count is UNKNOWN from this static pass; do not substitute a marketing GPU designation. Register ranges, raw GIC interrupt cells, clocks, power domains and provider arguments are recorded per node.
- **Stock artifact:** `mali_kbase_mt6878_r44.ko`, `mali_mgm_mt6878_r44.ko`, `mali_prot_alloc_mt6878_r44.ko`, `ged.ko`, `mtk_gpu_hal.ko`, `mtk_gpu_qos.ko`, `mtk_gpufreq_wrapper.ko`, `mtk_gpufreq_mt6878.ko`
- **Interfaces:** Kbase memory/context/queue management and mmap/ioctl paths; MGM memory groups and protected allocator; GED, GPU HAL callbacks, GPU QoS and gpufreq wrapper/platform interfaces. Trace kbase context creation → GPU VA allocation/import/map → CSF scheduling → completion/fault cleanup; then protected allocation and normal-world secure-heap calls. `/dev/mali0` is the expected Kbase ABI, not a newly observed binding. Numeric commands and layouts must be checked against stock handlers; source definitions alone are not parity.
- **Still required:** Complete per-module source/parity and observable DT/ABI acceptance; proprietary algorithms excluded

**Purpose:** Mali GPU normal-world kernel source/parity closure, not firmware reconstruction.

**Decision:** REGISTER PARTIAL. Active KMD/MGM/protected allocation had no owner. GED, GPU HAL/QoS and gpufreq candidates were generic platform-source triage, not a DONE parity scope; no distinct DONE component owns them.

**Entry point:** [CLAUDE-HANDOFF.md](CLAUDE-HANDOFF.md). Canonical research: `reverse-engineering/accelerator-preparation/MALI-GPU-KERNEL/`. Workspace pack: `Reverse Engineer - PARTIAL/MALI-GPU-KERNEL/`.

**Exclusive primary kernel modules (8):** `mali_kbase_mt6878_r44.ko`, `mali_mgm_mt6878_r44.ko`, `mali_prot_alloc_mt6878_r44.ko`, `ged.ko`, `mtk_gpu_hal.ko`, `mtk_gpu_qos.ko`, `mtk_gpufreq_wrapper.ko`, `mtk_gpufreq_mt6878.ko`. Dependencies are references, not additional ownership.

[stock modules](stock-modules.tsv), [DT nodes](dt-nodes.tsv), [source candidates](source-candidates.tsv), [parity gaps](parity-gaps.tsv), [imports](imports.tsv), [exports](exports.tsv), [functions](functions.tsv), [data symbols](data-symbols.tsv), [donor ABI witnesses](abi-source-witnesses.tsv).

Do not absorb mtk_gpu_power_throttling (THERMAL-POWER-HAL), mtk_sec_heap/tmem_ffa (TMEM-FFA), GenieZone transport/secure memory (existing GZ scopes), or the DONE mailbox/IPI providers. GPUEB host client belongs to GPU-AI-AUX-KERNEL-INTERFACES. mali_dmabuf_test is diagnostic stock baggage, not an additional unfinished accelerator. Retain Mali EGL/GLES/Vulkan blobs and stock mali_csffw.bin; their algorithms are not kernel parity.

No module rebuilt, hardware command executed or parity result created by this preparation. Published proof rows are preserved and labeled by axis; the component starts PARTIAL, never DONE.
