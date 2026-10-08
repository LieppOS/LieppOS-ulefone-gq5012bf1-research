# Proprietary boundary — MALI-GPU-KERNEL

Do not absorb mtk_gpu_power_throttling (THERMAL-POWER-HAL), mtk_sec_heap/tmem_ffa (TMEM-FFA), GenieZone transport/secure memory (existing GZ scopes), or the DONE mailbox/IPI providers. GPUEB host client belongs to GPU-AI-AUX-KERNEL-INTERFACES. mali_dmabuf_test is diagnostic stock baggage, not an additional unfinished accelerator. Retain Mali EGL/GLES/Vulkan blobs and stock mali_csffw.bin; their algorithms are not kernel parity.

[firmware metadata](firmware-boundaries.tsv) records paths, sizes and hashes only. Its historical coverage-loader labels are not loader implementation proofs; trace each real source/stock host loader separately. A signed scatter image is not necessarily loaded by Linux `request_firmware`. Code/data in remote images, secure-world functions, model/3A/tuning/PQ algorithms, per-unit calibration and signing keys are outside kernel-source parity.

No proprietary `.ko`, `.bin`, `.img`, calibration, Android HAL/library payload or raw dump enters this preparation tree or Git. Reuse private local artifacts by exact path/hash.

GPU runtime model/revision, OEM donor deltas, secure/protected execution and real frame performance remain unproved. No measured target source build exists for these eight modules.
