# Provenance — APUSYS-NPU-KERNEL

Prepared from exact stock module hashes, the merged stock DT, stock load/dep metadata and public pinned source. Qwen's 2026-10-08 preparation established ownership and fixed operands; this closure adds source reconstruction, independent builds and full acceptance without deleting the preparation inventories.

Accepted source repository: `/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_apusys_ulefone_gq5012bf1`, commit `924f66b779a64ae0b05f89e233ff2317866050ba`. It has no remote and was not pushed. Backup bundle and pins are under `source/`.

Independent verification used a fresh clone `/home/armol/kernel-work/apusys-npu-cleancheck/repo` and fresh workspace, with public inputs restored from an offline mirror. B1 and B2 independently recreated source, kout, natural provider CRCs, all target objects and both modules. `evidence/reconstruction/` is copied from that run and hash-indexed.

No stock `.ko`, proprietary firmware/userspace code, raw calibration, key, or device capture is committed as source. No device action occurred. The sole raw ELF residue is each module's 20-byte build-ID descriptor.
