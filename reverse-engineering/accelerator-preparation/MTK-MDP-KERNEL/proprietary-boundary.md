# Proprietary boundary — MTK-MDP-KERNEL

MEDIATEK-DRM remains DONE for its explicitly proved DRM/panel modules; that result does not close mdp_drv or either MML binary. Generic mtk-cmdq-drv-ext/cmdq-platform/helpers remain platform dependencies; cmdq-sec-drv remains the existing GZ-TZ-SYSTEM scope. Do not absorb video codec or camera ISP owners. Preserve userspace PQ algorithms as proprietary.

[firmware metadata](firmware-boundaries.tsv) records paths, sizes and hashes only. Its historical coverage-loader labels are not loader implementation proofs; trace each real source/stock host loader separately. A signed scatter image is not necessarily loaded by Linux `request_firmware`. Code/data in remote images, secure-world functions, model/3A/tuning/PQ algorithms, per-unit calibration and signing keys are outside kernel-source parity.

No proprietary `.ko`, `.bin`, `.img`, calibration, Android HAL/library payload or raw dump enters this preparation tree or Git. Reuse private local artifacts by exact path/hash.

No existing complete MDP/MML source-parity owner or measured rebuild was found. Public donor availability is not proof that hardware behavior or shipped module bytes match.
