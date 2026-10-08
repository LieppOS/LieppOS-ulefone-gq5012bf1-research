# Dependencies and singleton ownership — MALI-GPU-KERNEL

**Prerequisites:** GKI-KMI-BASELINE; TMEM-FFA; GZ-TRANSPORT; MTK-TINYSYS-IPI; GPUEB client ABI.

**Owned modules:** `mali_kbase_mt6878_r44.ko`, `mali_mgm_mt6878_r44.ko`, `mali_prot_alloc_mt6878_r44.ko`, `ged.ko`, `mtk_gpu_hal.ko`, `mtk_gpu_qos.ko`, `mtk_gpufreq_wrapper.ko`, `mtk_gpufreq_mt6878.ko`.

Do not absorb mtk_gpu_power_throttling (THERMAL-POWER-HAL), mtk_sec_heap/tmem_ffa (TMEM-FFA), GenieZone transport/secure memory (existing GZ scopes), or the DONE mailbox/IPI providers. GPUEB host client belongs to GPU-AI-AUX-KERNEL-INTERFACES. mali_dmabuf_test is diagnostic stock baggage, not an additional unfinished accelerator. Retain Mali EGL/GLES/Vulkan blobs and stock mali_csffw.bin; their algorithms are not kernel parity.

[Master dependency edges](../dependency-edges.tsv) resolve stock imports by symbol and CRC; each row carries consumer/provider/owner. The load order and legacy modinfo dependencies are recorded separately in stock-modules.tsv. `modules.dep` can be transitive and legacy modinfo can name obsolete provider identities; neither overrides the actual export/CRC graph.

Raw direct modinfo dependency sets: `aee_aed,irq-dbg,mtk_gpufreq_wrapper,ged,mtk_gpu_hal,tinysys-scmi,mrdump,emi,mtk_sec_heap,tmem_ffa; emi; mtk_gpufreq_wrapper,mtk_gpu_hal,system_heap,mediatek-drm,gpueb,mtk_tinysys_ipi,sspm_v3,mtk_gpu_qos; mtk_gpu_hal,mtk_gpufreq_wrapper,mtk_qos; gpueb,mtk_tinysys_ipi,mtk_gpu_hal,mtk_pbm,device-apc-common; mtk_gpufreq_wrapper,mrdump`. These names are not a list of new targets. UNKNOWN provider/type provenance must be resolved against existing stock export/KMI ledgers, not fabricated. Preserve generic platform providers and explicitly closed modules.

For cycles, freeze mutually shared headers/provider ABI, use unchanged stock provider operands during initial isolation, then verify the assembled reconstructed graph; copied stock symvers is an oracle, not source/type proof.
